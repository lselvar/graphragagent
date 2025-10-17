# GraphRAG Agent - Project Overview

## 📋 Project Summary

A production-ready full-stack application that implements **Graph RAG (Retrieval-Augmented Generation)** using:
- **Neo4j** for graph-based document storage
- **Google Gemini LLM** for intelligent responses
- **Sentence Transformers** for embeddings
- **FastAPI** for the backend API
- **React + Vite** for the frontend UI

## 🎯 What This Application Does

1. **Upload Documents** - Users can upload PDF, DOCX, or TXT files
2. **Process & Store** - Documents are chunked, embedded, and stored in a graph database
3. **Intelligent Search** - Vector similarity search finds relevant content
4. **AI Responses** - Gemini LLM generates contextual answers with source attribution

## 🏗️ Technical Architecture

### Backend Stack
```
FastAPI (Web Framework)
    ↓
Neo4j (Graph Database)
    ↓
Sentence Transformers (Embeddings)
    ↓
Google Gemini (LLM)
```

### Frontend Stack
```
React 18 (UI Framework)
    ↓
Vite (Build Tool)
    ↓
TailwindCSS (Styling)
    ↓
Axios (API Client)
```

## 📁 Project Structure

```
graphragagent/
│
├── backend/                      # Python Backend
│   ├── __init__.py
│   ├── config.py                # Settings & configuration
│   ├── main.py                  # FastAPI app & endpoints
│   ├── models.py                # Pydantic data models
│   ├── graph_store.py           # Neo4j operations
│   ├── embeddings.py            # Embedding generation
│   ├── document_processor.py    # Document processing
│   └── gemini_agent.py          # Gemini LLM integration
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js        # API client
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx      # Chat UI
│   │   │   ├── DocumentUpload.jsx     # Upload UI
│   │   │   └── DocumentList.jsx       # Document management
│   │   ├── App.jsx              # Main app component
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── pyproject.toml               # Python dependencies (Poetry)
├── docker-compose.yml           # Neo4j setup
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── start.sh                     # Startup script
├── README.md                    # Main documentation
├── SETUP.md                     # Quick setup guide
├── GETTING_STARTED.md           # User guide
└── PROJECT_OVERVIEW.md          # This file
```

## 🔄 Data Flow

### Document Upload Flow
```
1. User uploads document (PDF/DOCX/TXT)
   ↓
2. Backend extracts text
   ↓
3. Text is split into chunks (~1000 chars)
   ↓
4. Each chunk is embedded (384-dim vector)
   ↓
5. Chunks stored in Neo4j with relationships
   ↓
6. Success response to frontend
```

### Query Flow
```
1. User asks a question
   ↓
2. Question is embedded (384-dim vector)
   ↓
3. Vector similarity search in Neo4j
   ↓
4. Top 5 relevant chunks retrieved
   ↓
5. Chunks + question sent to Gemini
   ↓
6. Gemini generates contextual answer
   ↓
7. Response with sources shown to user
```

## 🔑 Key Components

### 1. Graph Store (`backend/graph_store.py`)
- Manages Neo4j connections
- Stores documents and chunks as nodes
- Creates relationships between chunks
- Performs vector similarity search
- Handles CRUD operations

### 2. Embedding Service (`backend/embeddings.py`)
- Uses Sentence Transformers
- Generates 384-dimensional embeddings
- Batch processing for efficiency
- Local model (no API calls)

### 3. Document Processor (`backend/document_processor.py`)
- Extracts text from various formats
- Chunks text with overlap
- Generates embeddings
- Stores in graph database
- Creates sequential relationships

### 4. Gemini Agent (`backend/gemini_agent.py`)
- Integrates Google Gemini API
- Formats context from retrieved chunks
- Manages conversation history
- Generates contextual responses
- Handles error cases

### 5. FastAPI Main (`backend/main.py`)
- Defines REST API endpoints
- Handles file uploads
- Manages chat requests
- CORS configuration
- Error handling

### 6. React Components
- **ChatInterface**: Real-time chat with AI
- **DocumentUpload**: Drag-and-drop upload
- **DocumentList**: Document management
- **App**: Main layout and routing

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
GOOGLE_API_KEY=your_key_here
NEO4J_PASSWORD=password123

# Optional (with defaults)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
GEMINI_MODEL=gemini-1.5-pro
TEMPERATURE=0.7
MAX_TOKENS=2048
```

### Poetry Dependencies (pyproject.toml)
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **google-genai**: Gemini API
- **neo4j**: Graph database driver
- **langchain**: Text processing
- **sentence-transformers**: Embeddings
- **pypdf**: PDF processing
- **python-docx**: DOCX processing

### NPM Dependencies (package.json)
- **react**: UI framework
- **vite**: Build tool
- **axios**: HTTP client
- **tailwindcss**: Styling
- **lucide-react**: Icons
- **react-markdown**: Markdown rendering

## 🚀 Deployment Considerations

### Backend
- Use **Gunicorn** or **Uvicorn** workers for production
- Set up **environment variables** securely
- Configure **CORS** for your domain
- Enable **logging** and monitoring
- Use **Redis** for caching (optional)

### Frontend
- Build with `npm run build`
- Serve with **Nginx** or **Vercel**
- Configure **API URL** for production
- Enable **HTTPS**
- Set up **CDN** for assets

### Database
- Use **Neo4j Aura** for managed hosting
- Or self-host with **persistent volumes**
- Configure **backups**
- Set up **monitoring**
- Optimize **indexes**

## 🔒 Security Considerations

1. **API Keys**: Never commit to Git, use environment variables
2. **CORS**: Configure allowed origins properly
3. **File Upload**: Validate file types and sizes
4. **Rate Limiting**: Implement for API endpoints
5. **Authentication**: Add user auth for production
6. **HTTPS**: Always use in production
7. **Input Validation**: Sanitize all user inputs

## 📊 Performance Optimization

### Backend
- **Batch embeddings** for multiple chunks
- **Connection pooling** for Neo4j
- **Async operations** where possible
- **Caching** for frequent queries
- **Index optimization** in Neo4j

### Frontend
- **Code splitting** with React.lazy
- **Image optimization**
- **Lazy loading** for components
- **Debouncing** for search inputs
- **Memoization** for expensive operations

## 🧪 Testing Strategy

### Backend Tests
```bash
poetry run pytest
```
- Unit tests for each module
- Integration tests for API endpoints
- Mock external services (Gemini, Neo4j)

### Frontend Tests
```bash
npm run test
```
- Component tests with React Testing Library
- Integration tests for user flows
- E2E tests with Playwright (optional)

## 📈 Monitoring & Observability

### Metrics to Track
- API response times
- Document processing time
- Embedding generation time
- Neo4j query performance
- Gemini API latency
- Error rates
- User activity

### Tools
- **Prometheus** for metrics
- **Grafana** for dashboards
- **Sentry** for error tracking
- **Neo4j monitoring** tools
- **FastAPI metrics** middleware

## 🔮 Future Enhancements

1. **Multi-user Support**: Add authentication and user management
2. **Document Collections**: Organize documents into collections
3. **Advanced Search**: Filters, date ranges, metadata search
4. **Export Features**: Export conversations and insights
5. **Batch Upload**: Upload multiple documents at once
6. **Document Preview**: View documents in the UI
7. **Analytics Dashboard**: Usage statistics and insights
8. **API Rate Limiting**: Protect against abuse
9. **Webhook Support**: Notifications for document processing
10. **Mobile App**: React Native mobile client

## 📚 Learning Resources

### Graph RAG
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [Neo4j Vector Search](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/)

### Gemini
- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Docs](https://ai.google.dev/docs)

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://docs.pydantic.dev/)

### React
- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Credits

Built with:
- FastAPI by Sebastián Ramírez
- React by Meta
- Neo4j by Neo4j, Inc.
- Gemini by Google
- Sentence Transformers by UKPLab

---

**Version**: 0.1.0  
**Last Updated**: October 2025  
**Status**: Production Ready
