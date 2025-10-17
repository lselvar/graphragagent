import os
import uuid
from typing import List, Dict, Any
from pathlib import Path
import logging
from datetime import datetime

import pypdf
from docx import Document as DocxDocument

from backend.config import settings
from backend.models import DocumentChunk
from backend.embeddings import embedding_service
from backend.graph_store import GraphStore

logger = logging.getLogger(__name__)


class SimpleTextSplitter:
    """Simple text splitter to replace langchain dependency."""
    
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        
        return chunks


class DocumentProcessor:
    """Process documents and store them in the graph database."""
    
    def __init__(self, graph_store: GraphStore):
        self.graph_store = graph_store
        self.text_splitter = SimpleTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        # Ensure upload directory exists
        Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
        return text
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise
        return text
    
    def extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from various file formats."""
        ext = Path(filename).suffix.lower()
        
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return self.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    async def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process a document: extract text, chunk, embed, and store in graph."""
        document_id = str(uuid.uuid4())
        
        try:
            # Extract text
            logger.info(f"Extracting text from {filename}")
            text = self.extract_text(file_path, filename)
            
            # Chunk text
            logger.info(f"Chunking text from {filename}")
            chunks = self.chunk_text(text)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Store document node
            metadata = {
                "filename": filename,
                "file_size": os.path.getsize(file_path),
                "num_chunks": len(chunks)
            }
            self.graph_store.store_document(document_id, filename, metadata)
            
            # Generate embeddings and store chunks
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = embedding_service.embed_texts(chunks)
            
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    chunk_id=f"{document_id}_chunk_{idx}",
                    document_id=document_id,
                    content=chunk_text,
                    chunk_index=idx,
                    embedding=embedding,
                    metadata={"position": idx, "length": len(chunk_text)}
                )
                self.graph_store.store_chunk(chunk)
            
            # Create sequential relationships between chunks
            for idx in range(len(chunks) - 1):
                source_id = f"{document_id}_chunk_{idx}"
                target_id = f"{document_id}_chunk_{idx + 1}"
                self.graph_store.create_relationship(
                    source_id, target_id, "NEXT", {"sequence": idx}
                )
            
            logger.info(f"Successfully processed document {filename}")
            
            return {
                "id": document_id,
                "filename": filename,
                "size": os.path.getsize(file_path),
                "uploaded_at": datetime.now(),
                "chunks_created": len(chunks),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
