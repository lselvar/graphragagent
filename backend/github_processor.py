import os
import uuid
import shutil
from typing import List, Dict, Any
from pathlib import Path
import logging
from datetime import datetime
import tempfile

from git import Repo

from backend.config import settings
from backend.document_processor import SimpleTextSplitter
from backend.models import DocumentChunk
from backend.embeddings import embedding_service
from backend.graph_store import GraphStore

logger = logging.getLogger(__name__)


class GitHubProcessor:
    """Process GitHub repositories and store code in the graph database."""
    
    # Code file extensions to process
    CODE_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
        '.html', '.css', '.scss', '.sass', '.vue', '.sql', '.sh', '.bash',
        '.yaml', '.yml', '.json', '.xml', '.md', '.txt', '.env', '.toml',
        '.ini', '.cfg', '.conf', '.dockerfile', '.makefile', '.gradle'
    }
    
    # Directories to skip
    SKIP_DIRS = {
        '.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env',
        'dist', 'build', 'target', '.idea', '.vscode', 'coverage',
        '.pytest_cache', '.mypy_cache', 'vendor', 'packages'
    }
    
    def __init__(self, graph_store: GraphStore):
        self.graph_store = graph_store
        self.text_splitter = SimpleTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    def _is_valid_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        # Check extension
        if file_path.suffix.lower() not in self.CODE_EXTENSIONS:
            return False
        
        # Check if in skip directory
        for part in file_path.parts:
            if part in self.SKIP_DIRS:
                return False
        
        # Check file size (skip files > 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return False
        except:
            return False
        
        return True
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL."""
        # Handle various GitHub URL formats
        # https://github.com/user/repo.git
        # https://github.com/user/repo
        # git@github.com:user/repo.git
        
        repo_url = repo_url.rstrip('/')
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        parts = repo_url.replace(':', '/').split('/')
        return parts[-1] if parts else 'unknown-repo'
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding."""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
                return ""
    
    def _get_file_language(self, file_path: Path) -> str:
        """Determine programming language from file extension."""
        ext_to_lang = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'React JSX',
            '.ts': 'TypeScript',
            '.tsx': 'React TSX',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.vue': 'Vue',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown',
        }
        return ext_to_lang.get(file_path.suffix.lower(), 'Text')
    
    async def process_repository(self, repo_url: str) -> Dict[str, Any]:
        """Clone and process a GitHub repository."""
        temp_dir = None
        document_id = str(uuid.uuid4())
        
        try:
            # Extract repo name
            repo_name = self._extract_repo_name(repo_url)
            logger.info(f"Processing GitHub repository: {repo_name} from {repo_url}")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix=f"graphrag_repo_{document_id}_")
            logger.info(f"Cloning repository to {temp_dir}")
            
            # Clone repository
            try:
                Repo.clone_from(repo_url, temp_dir, depth=1)
            except Exception as e:
                logger.error(f"Failed to clone repository: {e}")
                raise ValueError(f"Failed to clone repository. Please check the URL and ensure it's accessible: {str(e)}")
            
            # Find all code files
            repo_path = Path(temp_dir)
            code_files = []
            
            for file_path in repo_path.rglob('*'):
                if file_path.is_file() and self._is_valid_file(file_path):
                    code_files.append(file_path)
            
            logger.info(f"Found {len(code_files)} code files to process")
            
            if not code_files:
                raise ValueError("No processable code files found in repository")
            
            # Store repository document
            metadata = {
                "repo_url": repo_url,
                "repo_name": repo_name,
                "file_count": len(code_files),
                "num_chunks": 0  # Will update later
            }
            self.graph_store.store_document(document_id, f"GitHub: {repo_name}", metadata)
            
            # Process each file
            all_chunks = []
            total_chunks = 0
            
            for file_path in code_files:
                try:
                    # Read file content
                    content = self._read_file_content(file_path)
                    if not content.strip():
                        continue
                    
                    # Get relative path
                    rel_path = file_path.relative_to(repo_path)
                    language = self._get_file_language(file_path)
                    
                    # Add file header to content
                    file_header = f"# File: {rel_path}\n# Language: {language}\n# Lines: {len(content.splitlines())}\n\n"
                    full_content = file_header + content
                    
                    # Chunk the file
                    chunks = self.text_splitter.split_text(full_content)
                    
                    for idx, chunk_text in enumerate(chunks):
                        chunk_data = {
                            'text': chunk_text,
                            'file_path': str(rel_path),
                            'language': language,
                            'chunk_index': idx,
                            'file_chunk_index': idx
                        }
                        all_chunks.append(chunk_data)
                        total_chunks += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {e}")
                    continue
            
            logger.info(f"Created {total_chunks} chunks from {len(code_files)} files")
            
            # Update document with chunk count
            metadata['num_chunks'] = total_chunks
            self.graph_store.store_document(document_id, f"GitHub: {repo_name}", metadata)
            
            # Generate embeddings for all chunks
            logger.info(f"Generating embeddings for {total_chunks} chunks")
            chunk_texts = [chunk['text'] for chunk in all_chunks]
            embeddings = embedding_service.embed_texts(chunk_texts)
            
            # Store chunks in graph
            for idx, (chunk_data, embedding) in enumerate(zip(all_chunks, embeddings)):
                chunk = DocumentChunk(
                    chunk_id=f"{document_id}_chunk_{idx}",
                    document_id=document_id,
                    content=chunk_data['text'],
                    chunk_index=idx,
                    embedding=embedding,
                    metadata={
                        "file_path": chunk_data['file_path'],
                        "language": chunk_data['language'],
                        "file_chunk_index": chunk_data['file_chunk_index']
                    }
                )
                # Flatten metadata for Neo4j
                self.graph_store.store_chunk(chunk)
            
            # Create relationships between consecutive chunks from same file
            for i in range(len(all_chunks) - 1):
                if all_chunks[i]['file_path'] == all_chunks[i + 1]['file_path']:
                    source_id = f"{document_id}_chunk_{i}"
                    target_id = f"{document_id}_chunk_{i + 1}"
                    self.graph_store.create_relationship(
                        source_id, target_id, "NEXT_IN_FILE", 
                        {"file_path": all_chunks[i]['file_path']}
                    )
            
            logger.info(f"Successfully processed repository {repo_name}")
            
            return {
                "id": document_id,
                "filename": f"GitHub: {repo_name}",
                "repo_url": repo_url,
                "repo_name": repo_name,
                "size": sum(f.stat().st_size for f in code_files),
                "file_count": len(code_files),
                "uploaded_at": datetime.now(),
                "chunks_created": total_chunks,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing repository: {e}")
            raise
        
        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory: {e}")
