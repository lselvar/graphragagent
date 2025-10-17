from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging
from backend.config import settings
from backend.models import DocumentChunk, GraphNode, GraphRelationship

logger = logging.getLogger(__name__)


class GraphStore:
    """Neo4j graph database manager for storing document embeddings and relationships."""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes for efficient querying."""
        with self.driver.session() as session:
            # Create indexes
            try:
                session.run(
                    "CREATE INDEX document_id_index IF NOT EXISTS FOR (d:Document) ON (d.id)"
                )
                session.run(
                    "CREATE INDEX chunk_id_index IF NOT EXISTS FOR (c:Chunk) ON (c.id)"
                )
                logger.info("Created basic indexes successfully")
            except Exception as e:
                logger.warning(f"Error creating indexes: {e}")
            
            # Try to create vector index if supported (Neo4j 5.11+)
            try:
                session.run(
                    "CREATE VECTOR INDEX chunk_embedding_index IF NOT EXISTS "
                    "FOR (c:Chunk) ON (c.embedding) "
                    "OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}"
                )
                self.vector_index_available = True
                logger.info("Vector index created successfully")
            except Exception as e:
                logger.warning(f"Vector index not available (requires Neo4j 5.11+): {e}")
                self.vector_index_available = False
    
    def close(self):
        """Close the database connection."""
        self.driver.close()
    
    def store_document(self, document_id: str, filename: str, metadata: Dict[str, Any]) -> None:
        """Store a document node in the graph."""
        with self.driver.session() as session:
            # Flatten metadata to individual properties (Neo4j doesn't support nested maps)
            session.run(
                """
                MERGE (d:Document {id: $document_id})
                SET d.filename = $filename,
                    d.uploaded_at = datetime(),
                    d.file_size = $file_size,
                    d.num_chunks = $num_chunks,
                    d.repo_url = $repo_url,
                    d.repo_name = $repo_name,
                    d.file_count = $file_count
                """,
                document_id=document_id,
                filename=filename,
                file_size=metadata.get('file_size', 0),
                num_chunks=metadata.get('num_chunks', 0),
                repo_url=metadata.get('repo_url', ''),
                repo_name=metadata.get('repo_name', ''),
                file_count=metadata.get('file_count', 0)
            )
    
    def store_chunk(self, chunk: DocumentChunk) -> None:
        """Store a document chunk with its embedding in the graph."""
        with self.driver.session() as session:
            # Flatten metadata to individual properties (Neo4j doesn't support nested maps)
            metadata = chunk.metadata or {}
            session.run(
                """
                MERGE (c:Chunk {id: $chunk_id})
                SET c.content = $content,
                    c.chunk_index = $chunk_index,
                    c.embedding = $embedding,
                    c.position = $position,
                    c.length = $length,
                    c.file_path = $file_path,
                    c.language = $language,
                    c.file_chunk_index = $file_chunk_index
                WITH c
                MATCH (d:Document {id: $document_id})
                MERGE (c)-[:BELONGS_TO]->(d)
                """,
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                embedding=chunk.embedding,
                position=metadata.get('position', 0),
                length=metadata.get('length', 0),
                file_path=metadata.get('file_path', ''),
                language=metadata.get('language', ''),
                file_chunk_index=metadata.get('file_chunk_index', 0)
            )
    
    def create_relationship(self, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any] = None) -> None:
        """Create a relationship between two chunks."""
        properties = properties or {}
        with self.driver.session() as session:
            session.run(
                f"""
                MATCH (s:Chunk {{id: $source_id}})
                MATCH (t:Chunk {{id: $target_id}})
                MERGE (s)-[r:{rel_type}]->(t)
                SET r += $properties
                """,
                source_id=source_id,
                target_id=target_id,
                properties=properties
            )
    
    def vector_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform vector similarity search on chunk embeddings."""
        with self.driver.session() as session:
            # Try vector index first if available
            if hasattr(self, 'vector_index_available') and self.vector_index_available:
                try:
                    result = session.run(
                        """
                        CALL db.index.vector.queryNodes('chunk_embedding_index', $top_k, $query_embedding)
                        YIELD node, score
                        MATCH (node)-[:BELONGS_TO]->(d:Document)
                        RETURN node.id as chunk_id,
                               node.content as content,
                               node.chunk_index as chunk_index,
                               d.filename as filename,
                               d.id as document_id,
                               score
                        ORDER BY score DESC
                        """,
                        query_embedding=query_embedding,
                        top_k=top_k
                    )
                    return [dict(record) for record in result]
                except Exception as e:
                    logger.warning(f"Vector index query failed, using fallback: {e}")
            
            # Fallback: manual cosine similarity calculation
            logger.info("Using manual similarity calculation (slower)")
            result = session.run(
                """
                MATCH (c:Chunk)-[:BELONGS_TO]->(d:Document)
                WHERE c.embedding IS NOT NULL
                RETURN c.id as chunk_id,
                       c.content as content,
                       c.chunk_index as chunk_index,
                       c.embedding as embedding,
                       d.filename as filename,
                       d.id as document_id
                """,
            )
            
            # Calculate cosine similarity in Python
            import numpy as np
            chunks = [dict(record) for record in result]
            query_vec = np.array(query_embedding)
            
            for chunk in chunks:
                if chunk['embedding']:
                    chunk_vec = np.array(chunk['embedding'])
                    # Cosine similarity
                    similarity = np.dot(query_vec, chunk_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec))
                    chunk['score'] = float(similarity)
                else:
                    chunk['score'] = 0.0
                del chunk['embedding']  # Remove embedding from result
            
            # Sort by score and return top_k
            chunks.sort(key=lambda x: x['score'], reverse=True)
            return chunks[:top_k]
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Retrieve all chunks for a specific document."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Chunk)-[:BELONGS_TO]->(d:Document {id: $document_id})
                RETURN c.id as chunk_id,
                       c.content as content,
                       c.chunk_index as chunk_index,
                       c.position as position,
                       c.length as length
                ORDER BY c.chunk_index
                """,
                document_id=document_id
            )
            return [dict(record) for record in result]
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Retrieve all documents."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Document)
                OPTIONAL MATCH (c:Chunk)-[:BELONGS_TO]->(d)
                RETURN d.id as document_id,
                       d.filename as filename,
                       d.uploaded_at as uploaded_at,
                       d.file_size as file_size,
                       d.num_chunks as num_chunks,
                       count(c) as chunk_count
                ORDER BY d.uploaded_at DESC
                """
            )
            return [dict(record) for record in result]
    
    def delete_document(self, document_id: str) -> None:
        """Delete a document and all its chunks."""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (d:Document {id: $document_id})
                OPTIONAL MATCH (c:Chunk)-[:BELONGS_TO]->(d)
                DETACH DELETE c, d
                """,
                document_id=document_id
            )
    
    def get_related_chunks(self, chunk_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Get chunks related to a given chunk through graph relationships."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = (start:Chunk {id: $chunk_id})-[*1..%d]-(related:Chunk)
                RETURN DISTINCT related.id as chunk_id,
                       related.content as content,
                       related.chunk_index as chunk_index,
                       length(path) as distance
                ORDER BY distance
                LIMIT 10
                """ % max_depth,
                chunk_id=chunk_id
            )
            return [dict(record) for record in result]
