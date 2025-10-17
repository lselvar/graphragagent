# GraphRAG Agent - Setup & Verification Checklist

## ✅ Pre-Installation Checklist

### System Requirements
- [ ] Python 3.10 or higher installed
  ```bash
  python --version  # Should show 3.10+
  ```
- [ ] Node.js 18 or higher installed
  ```bash
  node --version  # Should show 18+
  ```
- [ ] Docker installed and running
  ```bash
  docker --version
  docker ps  # Should not error
  ```
- [ ] Poetry installed (for Python dependency management)
  ```bash
  poetry --version
  ```
  If not installed:
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

### API Access
- [ ] Google API Key obtained from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] Gemini API access enabled on your Google account
- [ ] API key tested and working

## 📦 Installation Checklist

### Step 1: Environment Configuration
- [ ] `.env` file created from `.env.example`
  ```bash
  cp .env.example .env
  ```
- [ ] `GOOGLE_API_KEY` added to `.env`
- [ ] `NEO4J_PASSWORD` set in `.env`
- [ ] All required environment variables configured

### Step 2: Database Setup
- [ ] Docker Compose file exists (`docker-compose.yml`)
- [ ] Neo4j container started
  ```bash
  docker-compose up -d
  ```
- [ ] Neo4j is running
  ```bash
  docker ps | grep neo4j
  ```
- [ ] Neo4j Browser accessible at http://localhost:7474
- [ ] Can login to Neo4j (username: `neo4j`, password from `.env`)

### Step 3: Backend Setup
- [ ] Poetry dependencies installed
  ```bash
  poetry install
  ```
- [ ] No installation errors
- [ ] All Python packages installed successfully
- [ ] `uploads/` directory will be created automatically

### Step 4: Frontend Setup
- [ ] Node modules installed
  ```bash
  cd frontend && npm install
  ```
- [ ] No installation errors
- [ ] All npm packages installed successfully

## 🚀 Startup Checklist

### Backend Startup
- [ ] Backend server starts without errors
  ```bash
  poetry run python -m backend.main
  ```
- [ ] Backend accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health check returns success
  ```bash
  curl http://localhost:8000/health
  ```
- [ ] No connection errors to Neo4j
- [ ] Embedding model downloads successfully (first run only)

### Frontend Startup
- [ ] Frontend dev server starts without errors
  ```bash
  cd frontend && npm run dev
  ```
- [ ] Frontend accessible at http://localhost:3000
- [ ] No console errors in browser
- [ ] UI loads correctly

## 🧪 Functionality Testing Checklist

### Document Upload Testing
- [ ] Navigate to Upload tab
- [ ] Drag and drop works
- [ ] Click to select works
- [ ] Can upload PDF file
- [ ] Can upload DOCX file
- [ ] Can upload TXT file
- [ ] Upload shows progress
- [ ] Success message appears
- [ ] Chunk count displayed
- [ ] File rejected if too large (>10MB)
- [ ] File rejected if wrong type

### Chat Interface Testing
- [ ] Navigate to Chat tab
- [ ] Input field is visible
- [ ] Can type message
- [ ] Send button works
- [ ] Loading indicator appears
- [ ] Response is received
- [ ] Response is formatted correctly
- [ ] Sources are displayed
- [ ] Can send multiple messages
- [ ] Conversation history maintained

### Document Management Testing
- [ ] Navigate to Documents tab
- [ ] Uploaded documents are listed
- [ ] Document count is correct
- [ ] Filename displayed correctly
- [ ] Chunk count shown
- [ ] Upload date shown
- [ ] Delete button works
- [ ] Confirmation dialog appears
- [ ] Document deleted successfully
- [ ] List updates after deletion
- [ ] Refresh button works

## 🔍 Verification Checklist

### Backend Verification
- [ ] API responds to requests
- [ ] Neo4j connection successful
- [ ] Embeddings generated correctly
- [ ] Documents stored in Neo4j
- [ ] Vector search returns results
- [ ] Gemini API calls successful
- [ ] Error handling works
- [ ] CORS configured correctly

### Frontend Verification
- [ ] All components render
- [ ] Navigation between tabs works
- [ ] API calls successful
- [ ] Error messages display
- [ ] Loading states work
- [ ] Responsive design works
- [ ] Icons display correctly
- [ ] Styling is correct

### Database Verification
- [ ] Neo4j Browser accessible
- [ ] Can execute Cypher queries
- [ ] Document nodes created
- [ ] Chunk nodes created
- [ ] Relationships exist
- [ ] Vector index created
- [ ] Queries return data

Run in Neo4j Browser:
```cypher
// Check documents
MATCH (d:Document) RETURN count(d)

// Check chunks
MATCH (c:Chunk) RETURN count(c)

// Check relationships
MATCH (c:Chunk)-[r:BELONGS_TO]->(d:Document)
RETURN count(r)

// Check indexes
SHOW INDEXES
```

## 🐛 Troubleshooting Checklist

### If Backend Fails to Start
- [ ] Check Python version (3.10+)
- [ ] Check Poetry installation
- [ ] Verify `.env` file exists
- [ ] Check Neo4j is running
- [ ] Verify Neo4j credentials
- [ ] Check port 8000 is available
- [ ] Review error logs
- [ ] Reinstall dependencies

### If Frontend Fails to Start
- [ ] Check Node.js version (18+)
- [ ] Check npm installation
- [ ] Verify package.json exists
- [ ] Check port 3000 is available
- [ ] Clear node_modules and reinstall
- [ ] Check backend is running
- [ ] Review console errors

### If Neo4j Connection Fails
- [ ] Check Docker is running
- [ ] Verify Neo4j container is up
- [ ] Check Neo4j logs
- [ ] Verify credentials in `.env`
- [ ] Check port 7687 is available
- [ ] Restart Neo4j container
- [ ] Check firewall settings

### If Gemini API Fails
- [ ] Verify API key is correct
- [ ] Check API key has Gemini access
- [ ] Check internet connection
- [ ] Verify no rate limiting
- [ ] Check API quota
- [ ] Review error messages

### If Embeddings Fail
- [ ] Check internet connection (first run)
- [ ] Verify model downloads
- [ ] Check disk space
- [ ] Clear model cache if needed
- [ ] Check Python version compatibility

## 📊 Performance Checklist

### Expected Performance
- [ ] Document upload: <10 seconds for 10-page PDF
- [ ] Embedding generation: <5 seconds for 100 chunks
- [ ] Vector search: <100ms
- [ ] Chat response: 3-6 seconds total
- [ ] Frontend load: <2 seconds

### If Performance is Slow
- [ ] Check system resources (CPU, RAM)
- [ ] Verify Neo4j has enough memory
- [ ] Check network latency to Gemini API
- [ ] Review document size
- [ ] Check chunk size settings
- [ ] Monitor Neo4j query performance

## 🔐 Security Checklist

### Development
- [ ] `.env` file not committed to Git
- [ ] `.gitignore` includes `.env`
- [ ] Neo4j password is strong
- [ ] API keys are secure
- [ ] CORS allows localhost only

### Production (Future)
- [ ] Use environment variables
- [ ] Enable HTTPS
- [ ] Configure proper CORS
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Use secrets management

## 📝 Documentation Checklist

### Files to Review
- [ ] README.md - Main documentation
- [ ] SETUP.md - Quick setup guide
- [ ] GETTING_STARTED.md - User guide
- [ ] ARCHITECTURE.md - Technical architecture
- [ ] PROJECT_OVERVIEW.md - Project details
- [ ] QUICK_REFERENCE.md - Command reference
- [ ] CHECKLIST.md - This file

### Understanding
- [ ] Understand project structure
- [ ] Know how to start services
- [ ] Know how to use the application
- [ ] Know where to find logs
- [ ] Know how to troubleshoot
- [ ] Know how to contribute

## 🎯 Ready to Use Checklist

### Final Verification
- [ ] All services running
- [ ] Can upload documents
- [ ] Can chat with documents
- [ ] Can manage documents
- [ ] No errors in logs
- [ ] Performance is acceptable
- [ ] UI is responsive
- [ ] All features work

### You're Ready When:
- [ ] ✅ Backend running on port 8000
- [ ] ✅ Frontend running on port 3000
- [ ] ✅ Neo4j running on port 7687
- [ ] ✅ Can upload and process documents
- [ ] ✅ Can query documents via chat
- [ ] ✅ Responses include sources
- [ ] ✅ No critical errors

## 🎉 Success Criteria

You've successfully set up GraphRAG Agent when:

1. ✅ All three services are running (Backend, Frontend, Neo4j)
2. ✅ You can upload a document successfully
3. ✅ The document is processed and chunked
4. ✅ You can ask questions about the document
5. ✅ You receive AI-generated responses with sources
6. ✅ The UI is responsive and error-free

## 📞 Getting Help

If you're stuck:

1. **Check the logs**
   - Backend: Terminal output
   - Frontend: Browser console
   - Neo4j: `docker-compose logs neo4j`

2. **Review documentation**
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands
   - [SETUP.md](SETUP.md) for setup help
   - [README.md](README.md) for detailed info

3. **Common issues**
   - Port conflicts: Change ports in config
   - Missing dependencies: Reinstall
   - API errors: Check API key
   - Database errors: Restart Neo4j

4. **Still stuck?**
   - Open an issue on GitHub
   - Include error logs
   - Describe what you tried

---

**Congratulations!** Once all checkboxes are complete, you have a fully functional GraphRAG Agent! 🚀
