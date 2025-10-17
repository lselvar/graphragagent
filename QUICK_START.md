# 🚀 Quick Start Guide - GraphRAG Agent

## Prerequisites

- Python 3.10+
- Node.js 16+
- Docker (for Neo4j)
- Google API Key (for Gemini)

## 1. Setup Environment

### Clone and Install

```bash
cd /Users/lourdurajselvaraj/CascadeProjects/graphragagent

# Install Python dependencies
poetry install --no-root

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Configure Environment

Create `.env` file in project root:

```bash
# Google AI
GOOGLE_API_KEY=your_google_api_key_here

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# App Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
GEMINI_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.7
MAX_TOKENS=8192
UPLOAD_DIR=./uploads
```

## 2. Start Neo4j Database

```bash
# Start Neo4j with Docker
docker-compose up -d

# Verify Neo4j is running
# Open browser: http://localhost:7474
# Login with neo4j/your_password
```

## 3. Start Backend Server

```bash
# From project root
poetry run uvicorn backend.main:app --reload --port 8000

# Backend will be available at:
# http://localhost:8000
# API docs: http://localhost:8000/docs
```

## 4. Start Frontend (Optional)

```bash
cd frontend
npm run dev

# Frontend will be available at:
# http://localhost:5173
```

## 5. Test the System

### Test 1: Upload a Document

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/your/document.pdf"
```

### Test 2: Process GitHub Repository

```bash
curl -X POST http://localhost:8000/api/github/process \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/username/repo"}'
```

### Test 3: Chat with Knowledge Base

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What documents do you have?",
    "conversation_history": []
  }'
```

### Test 4: List Documents

```bash
curl http://localhost:8000/api/documents
```

## 6. Use with Claude Desktop (Optional)

### Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "graphrag-agent": {
      "command": "poetry",
      "args": ["run", "python", "run_mcp_server.py"],
      "cwd": "/Users/lourdurajselvaraj/CascadeProjects/graphragagent"
    }
  }
}
```

### Restart Claude Desktop

Close and reopen Claude Desktop completely.

### Test in Claude

In Claude Desktop, ask:
```
Can you list the documents in the GraphRAG knowledge base?
```

Claude will automatically use the MCP tools!

## 🎯 Common Use Cases

### Use Case 1: Analyze a Codebase

```bash
# 1. Process GitHub repo
curl -X POST http://localhost:8000/api/github/process \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/my-project"}'

# 2. Ask questions
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does this codebase do? What are the main components?",
    "conversation_history": []
  }'
```

### Use Case 2: Search Documentation

```bash
# 1. Upload documentation PDFs
curl -X POST http://localhost:8000/api/upload \
  -F "file=@docs/manual.pdf"

# 2. Search for specific information
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I configure authentication?",
    "conversation_history": []
  }'
```

### Use Case 3: Code Review Assistant

```bash
# Process multiple repos
curl -X POST http://localhost:8000/api/github/process \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/frontend"}'

curl -X POST http://localhost:8000/api/github/process \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/backend"}'

# Ask comparative questions
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare the authentication implementation in frontend and backend",
    "conversation_history": []
  }'
```

## 🔍 Verify Installation

### Check All Services

```bash
# 1. Check Neo4j
docker ps | grep neo4j

# 2. Check Backend
curl http://localhost:8000/health

# 3. Check Frontend (if running)
curl http://localhost:5173

# 4. Check Python imports
poetry run python -c "from backend.gemini_agent import GeminiAgent; print('✅ OK')"
```

### View Logs

```bash
# Backend logs (in terminal where uvicorn is running)

# Neo4j logs
docker logs neo4j

# Check Neo4j browser
# Open: http://localhost:7474
# Run query: MATCH (n) RETURN count(n)
```

## 🐛 Troubleshooting

### Issue: "Connection refused" to Neo4j

```bash
# Check if Neo4j is running
docker ps

# If not running, start it
docker-compose up -d

# Check logs
docker logs neo4j
```

### Issue: "Module not found"

```bash
# Reinstall dependencies
poetry install --no-root

# Verify installation
poetry run python -c "import google.adk; print('✅')"
```

### Issue: "Invalid API key"

```bash
# Check .env file exists
cat .env | grep GOOGLE_API_KEY

# Verify API key is valid
# Get key from: https://aistudio.google.com/apikey
```

### Issue: Frontend won't start

```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Try again
npm run dev
```

## 📊 Monitor System

### Neo4j Browser

```
URL: http://localhost:7474
User: neo4j
Password: your_password

# Useful queries:
MATCH (n) RETURN count(n)  # Count all nodes
MATCH (d:Document) RETURN d  # List documents
MATCH (c:Chunk) RETURN count(c)  # Count chunks
```

### API Documentation

```
URL: http://localhost:8000/docs

# Interactive Swagger UI
# Test all endpoints
# View request/response schemas
```

### Frontend

```
URL: http://localhost:5173

# Chat interface
# Upload documents
# View conversation history
```

## 🎓 Next Steps

1. **Upload your first document** - PDF, DOCX, or TXT
2. **Process a GitHub repository** - Your own or public repo
3. **Ask questions** - Test the chat interface
4. **Try Claude Desktop** - MCP integration
5. **Explore the code** - Understand the architecture

## 📚 Additional Resources

- **Full Documentation**: See `IMPLEMENTATION_STATUS.md`
- **ADK Guide**: See `GOOGLE_ADK_IMPLEMENTATION.md`
- **MCP Guide**: See `MCP_INTEGRATION.md`
- **API Reference**: http://localhost:8000/docs

## 🆘 Getting Help

1. Check logs in terminal
2. Review documentation files
3. Check Neo4j browser for data
4. Verify .env configuration
5. Test individual components

---

**Ready to go!** 🚀

Start with:
```bash
docker-compose up -d
poetry run uvicorn backend.main:app --reload
```

Then upload a document or process a GitHub repo!
