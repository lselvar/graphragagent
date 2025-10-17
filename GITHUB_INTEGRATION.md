# GitHub Repository Integration

## Overview

GraphRAG Agent now supports **GitHub repository ingestion**, allowing you to analyze and query code from any public GitHub repository using AI.

## Features

### 🔍 **Intelligent Code Analysis**
- Clone any public GitHub repository
- Process all code files automatically
- Generate embeddings for semantic code search
- Query code using natural language

### 📁 **Supported File Types**
- **Languages**: Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, and more
- **Web**: HTML, CSS, SCSS, Vue, React (JSX/TSX)
- **Config**: YAML, JSON, XML, TOML, INI
- **Docs**: Markdown, Text files
- **Scripts**: Shell, Bash, SQL

### 🚀 **Smart Processing**
- Automatically skips binary files and dependencies (`node_modules`, `.git`, etc.)
- Preserves file structure and context
- Maintains relationships between code chunks
- Adds file metadata (path, language, line numbers)

## How It Works

### 1. **Repository Cloning**
```
User provides GitHub URL
    ↓
Backend clones repository (shallow clone)
    ↓
Scans for processable code files
```

### 2. **Code Processing**
```
For each code file:
    ↓
Extract content with file metadata
    ↓
Split into chunks (~1000 chars)
    ↓
Generate embeddings (384-dim vectors)
    ↓
Store in Neo4j graph database
```

### 3. **Graph Storage**
```
Document Node: Repository info
    ↓
Chunk Nodes: Code chunks with metadata
    ↓
Relationships: BELONGS_TO, NEXT_IN_FILE
```

## Usage

### Frontend (React UI)

1. **Navigate to GitHub Tab**
   - Click on the "GitHub" tab in the UI

2. **Enter Repository URL**
   ```
   https://github.com/username/repository
   ```

3. **Process Repository**
   - Click "Process Repo" button
   - Wait for processing (may take 1-5 minutes)
   - See success message with stats

4. **Query the Code**
   - Go to Chat tab
   - Ask questions about the code
   - Get AI-powered answers with source attribution

### Example Queries

```
"What does this repository do?"
"Explain the main.py file"
"How is authentication implemented?"
"Show me the API endpoints"
"What dependencies does this project use?"
"Explain the database schema"
"How does the user registration work?"
"What testing framework is used?"
```

## Backend API

### Endpoint

```http
POST /api/github
Content-Type: application/json

{
  "repo_url": "https://github.com/username/repository"
}
```

### Response

```json
{
  "id": "uuid",
  "filename": "GitHub: repository-name",
  "repo_url": "https://github.com/username/repository",
  "repo_name": "repository-name",
  "size": 1234567,
  "file_count": 42,
  "uploaded_at": "2025-10-15T23:00:00",
  "chunks_created": 156,
  "status": "success"
}
```

### Error Responses

```json
{
  "detail": "Failed to clone repository. Please check the URL..."
}
```

## Implementation Details

### Backend Components

#### 1. **GitHubProcessor** (`backend/github_processor.py`)
- Handles repository cloning
- Filters code files
- Processes and chunks code
- Generates embeddings
- Stores in graph database

#### 2. **API Endpoint** (`backend/main.py`)
```python
@app.post("/api/github")
async def process_github_repo(request: GitHubRepoRequest):
    result = await github_processor.process_repository(request.repo_url)
    return DocumentUpload(**result)
```

#### 3. **Graph Storage** (`backend/graph_store.py`)
- Extended to store repository metadata
- Stores file paths and languages
- Creates file-based relationships

### Frontend Components

#### 1. **GitHubUpload** (`frontend/src/components/GitHubUpload.jsx`)
- URL input form
- Validation
- Processing status
- Success/error messages

#### 2. **API Client** (`frontend/src/api/client.js`)
```javascript
export const processGitHubRepo = async (repoUrl) => {
  const response = await apiClient.post('/api/github', {
    repo_url: repoUrl,
  });
  return response.data;
};
```

## Configuration

### Skipped Directories
```python
SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv',
    'dist', 'build', 'target', '.idea', '.vscode', 'coverage',
    '.pytest_cache', '.mypy_cache', 'vendor', 'packages'
}
```

### File Size Limit
- Maximum file size: 1MB
- Larger files are automatically skipped

### Chunk Settings
- Chunk size: 1000 characters (configurable in `.env`)
- Chunk overlap: 200 characters

## Graph Database Schema

### Document Node (Repository)
```cypher
(:Document {
  id: String,
  filename: String,  // "GitHub: repo-name"
  uploaded_at: DateTime,
  file_size: Integer,
  num_chunks: Integer,
  repo_url: String,
  repo_name: String,
  file_count: Integer
})
```

### Chunk Node (Code Chunk)
```cypher
(:Chunk {
  id: String,
  content: String,
  chunk_index: Integer,
  embedding: List[Float],  // 384 dimensions
  file_path: String,       // e.g., "src/main.py"
  language: String,        // e.g., "Python"
  file_chunk_index: Integer
})
```

### Relationships
```cypher
(:Chunk)-[:BELONGS_TO]->(:Document)
(:Chunk)-[:NEXT_IN_FILE {file_path: String}]->(:Chunk)
```

## Performance

### Processing Time
- **Small repos** (<50 files): 30-60 seconds
- **Medium repos** (50-200 files): 1-3 minutes
- **Large repos** (200+ files): 3-10 minutes

### Optimization
- Shallow clone (depth=1) for faster cloning
- Parallel embedding generation
- Efficient file filtering
- Automatic cleanup of temporary files

## Limitations

### Current Limitations
1. **Public repositories only** - Private repos require authentication
2. **File size limit** - Files >1MB are skipped
3. **No binary files** - Only text-based code files
4. **Single branch** - Only processes default branch

### Future Enhancements
1. Private repository support with authentication
2. Branch selection
3. Incremental updates
4. Code structure analysis
5. Dependency graph extraction

## Troubleshooting

### "Failed to clone repository"
- **Check URL**: Ensure it's a valid GitHub URL
- **Repository access**: Verify the repository is public
- **Network**: Check internet connection
- **Repository size**: Very large repos may timeout

### "No processable code files found"
- Repository may contain only binary files
- Check if repository has actual code files
- Verify file extensions are supported

### Processing takes too long
- Large repositories take time
- Check backend logs for progress
- Consider processing smaller repositories first

### Out of memory errors
- Very large repositories may exceed memory
- Increase system resources
- Process smaller repositories

## Security Considerations

### Safe Practices
- ✅ Only clones to temporary directories
- ✅ Automatic cleanup after processing
- ✅ No code execution
- ✅ Read-only operations
- ✅ Validates GitHub URLs

### What We DON'T Do
- ❌ Execute any code from repositories
- ❌ Store credentials
- ❌ Modify repositories
- ❌ Access private data

## Examples

### Example 1: Analyze a Python Project
```
URL: https://github.com/fastapi/fastapi
Queries:
- "How does FastAPI handle routing?"
- "Explain the dependency injection system"
- "What's the structure of the codebase?"
```

### Example 2: Understand a React App
```
URL: https://github.com/facebook/react
Queries:
- "How does React's reconciliation work?"
- "Explain the hooks implementation"
- "What's the fiber architecture?"
```

### Example 3: Learn from Documentation
```
URL: https://github.com/microsoft/vscode
Queries:
- "How is the extension API structured?"
- "Explain the editor architecture"
- "What's the build process?"
```

## Dependencies

### Python Packages
```toml
gitpython = "^3.1.40"  # For Git operations
```

### Installation
```bash
poetry add gitpython
poetry install
```

## Testing

### Test GitHub Integration
```bash
# Start backend
poetry run python -m backend.main

# Test with curl
curl -X POST http://localhost:8000/api/github \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/username/small-repo"}'
```

### Test in UI
1. Start frontend: `npm run dev`
2. Navigate to GitHub tab
3. Enter a small test repository URL
4. Verify processing completes
5. Query the code in Chat tab

## Best Practices

### For Users
1. **Start small**: Test with smaller repositories first
2. **Be patient**: Large repos take time to process
3. **Specific queries**: Ask specific questions about the code
4. **Use context**: Reference file names in your questions

### For Developers
1. **Monitor logs**: Check backend logs for processing status
2. **Handle errors**: Implement proper error handling
3. **Optimize chunks**: Adjust chunk size for your use case
4. **Clean up**: Ensure temporary files are deleted

## Resources

- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [GitHub API](https://docs.github.com/en/rest)
- [Neo4j Graph Database](https://neo4j.com/docs/)

---

**Status**: ✅ Fully Implemented and Tested  
**Version**: 0.3.0  
**Date**: October 15, 2025  
**Feature**: GitHub Repository Integration
