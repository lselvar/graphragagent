# Quick Reference Guide

## 🚀 Quick Start Commands

### First Time Setup
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 2. Start Neo4j
docker-compose up -d

# 3. Install dependencies
poetry install
cd frontend && npm install && cd ..

# 4. Start everything
./start.sh
```

### Daily Development
```bash
# Terminal 1 - Backend
poetry run python -m backend.main

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## 📍 Important URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Neo4j Browser | http://localhost:7474 | neo4j / password123 |

## 🔑 Environment Variables

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here
NEO4J_PASSWORD=password123

# Optional (defaults shown)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
GEMINI_MODEL=gemini-1.5-pro
TEMPERATURE=0.7
MAX_TOKENS=2048
```

## 🛠️ Common Commands

### Backend
```bash
# Run server
poetry run python -m backend.main

# Run with auto-reload
poetry run uvicorn backend.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black backend/

# Type checking
poetry run mypy backend/

# Add dependency
poetry add package-name

# Update dependencies
poetry update
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Add dependency
npm install package-name

# Update dependencies
npm update
```

### Docker
```bash
# Start Neo4j
docker-compose up -d

# Stop Neo4j
docker-compose down

# View logs
docker-compose logs -f neo4j

# Restart Neo4j
docker-compose restart

# Remove volumes (clean slate)
docker-compose down -v
```

## 📁 File Locations

### Configuration Files
- `.env` - Environment variables
- `pyproject.toml` - Python dependencies
- `frontend/package.json` - Node dependencies
- `docker-compose.yml` - Neo4j setup

### Backend Code
- `backend/main.py` - API endpoints
- `backend/config.py` - Settings
- `backend/graph_store.py` - Neo4j operations
- `backend/gemini_agent.py` - LLM integration
- `backend/embeddings.py` - Embedding service
- `backend/document_processor.py` - Document processing

### Frontend Code
- `frontend/src/App.jsx` - Main app
- `frontend/src/components/ChatInterface.jsx` - Chat UI
- `frontend/src/components/DocumentUpload.jsx` - Upload UI
- `frontend/src/components/DocumentList.jsx` - Document list
- `frontend/src/api/client.js` - API client

## 🔧 API Endpoints

### Document Management
```bash
# Upload document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"

# List documents
curl http://localhost:8000/api/documents

# Delete document
curl -X DELETE http://localhost:8000/api/documents/{id}

# Get document chunks
curl http://localhost:8000/api/documents/{id}/chunks
```

### Chat
```bash
# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is this document about?"}'
```

### Health Check
```bash
# Check API health
curl http://localhost:8000/health

# Check API info
curl http://localhost:8000/
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check Neo4j is running
docker ps | grep neo4j

# Check environment variables
cat .env

# Reinstall dependencies
poetry install --no-cache
```

### Frontend won't start
```bash
# Check if port 3000 is in use
lsof -i :3000

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check backend is running
curl http://localhost:8000/health
```

### Neo4j connection issues
```bash
# Check Neo4j status
docker-compose ps

# View Neo4j logs
docker-compose logs neo4j

# Restart Neo4j
docker-compose restart neo4j

# Reset Neo4j (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Embedding model issues
```bash
# Clear cache and re-download
rm -rf ~/.cache/torch/sentence_transformers/

# Run again
poetry run python -m backend.main
```

## 📊 Neo4j Queries

### Useful Cypher Queries
```cypher
// Count all documents
MATCH (d:Document) RETURN count(d)

// Count all chunks
MATCH (c:Chunk) RETURN count(c)

// View document structure
MATCH (d:Document)<-[:BELONGS_TO]-(c:Chunk)
RETURN d.filename, count(c) as chunks

// Find chunks by content
MATCH (c:Chunk)
WHERE c.content CONTAINS "search term"
RETURN c.content, c.chunk_index

// Delete all data (WARNING)
MATCH (n) DETACH DELETE n

// View indexes
SHOW INDEXES
```

## 🔍 Debugging Tips

### Backend Debugging
```python
# Add logging
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")

# Check Neo4j connection
from backend.graph_store import GraphStore
store = GraphStore()
# Should not raise error

# Test embedding service
from backend.embeddings import embedding_service
emb = embedding_service.embed_text("test")
print(len(emb))  # Should be 384
```

### Frontend Debugging
```javascript
// Check API connection
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)

// View API responses
console.log('API Response:', response)

// Check environment variables
console.log(import.meta.env)
```

## 📈 Performance Tips

### Backend Optimization
- Use batch embedding for multiple chunks
- Enable Neo4j connection pooling
- Cache frequent queries
- Use async operations

### Frontend Optimization
- Lazy load components
- Debounce search inputs
- Optimize re-renders with React.memo
- Use code splitting

## 🔐 Security Checklist

- [ ] Never commit `.env` file
- [ ] Use strong Neo4j password
- [ ] Keep API keys secure
- [ ] Configure CORS properly
- [ ] Validate file uploads
- [ ] Sanitize user inputs
- [ ] Use HTTPS in production
- [ ] Implement rate limiting

## 📝 Code Style

### Python (Backend)
```python
# Use Black formatter
poetry run black backend/

# Follow PEP 8
# Use type hints
def function_name(param: str) -> int:
    return len(param)
```

### JavaScript (Frontend)
```javascript
// Use ESLint
npm run lint

// Use functional components
const Component = () => {
  return <div>Content</div>
}

// Use hooks
const [state, setState] = useState(initial)
```

## 🚢 Deployment Checklist

### Pre-deployment
- [ ] Run tests
- [ ] Build frontend
- [ ] Update environment variables
- [ ] Configure CORS
- [ ] Set up monitoring
- [ ] Enable HTTPS
- [ ] Configure backups

### Production Environment
```bash
# Backend
poetry run gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
npm run build
# Serve dist/ folder with Nginx or CDN
```

## 📚 Additional Resources

- [Full README](README.md)
- [Setup Guide](SETUP.md)
- [Getting Started](GETTING_STARTED.md)
- [Architecture](ARCHITECTURE.md)
- [Project Overview](PROJECT_OVERVIEW.md)

## 💡 Tips & Tricks

1. **Use the startup script**: `./start.sh` starts everything
2. **Check logs**: Backend logs show processing details
3. **Use Neo4j Browser**: Visualize your graph data
4. **Test with small files**: Start with simple text files
5. **Monitor API docs**: http://localhost:8000/docs for interactive API testing

---

**Need Help?** Check the troubleshooting section or open an issue on GitHub.
