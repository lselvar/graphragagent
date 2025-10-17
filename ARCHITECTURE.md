# GraphRAG Agent - Architecture Documentation

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Upload     │  │     Chat     │  │  Documents   │        │
│  │   Component  │  │  Component   │  │  Component   │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                │
│                            │                                    │
│                    ┌───────▼────────┐                          │
│                    │  React App     │                          │
│                    │  (Port 3000)   │                          │
│                    └───────┬────────┘                          │
└────────────────────────────┼───────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │
┌────────────────────────────▼───────────────────────────────────┐
│                      BACKEND API LAYER                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              FastAPI Application                          │ │
│  │                  (Port 8000)                              │ │
│  │                                                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │   Upload    │  │    Chat     │  │  Document   │     │ │
│  │  │  Endpoint   │  │  Endpoint   │  │  Endpoints  │     │ │
│  │  └─────┬───────┘  └─────┬───────┘  └─────┬───────┘     │ │
│  └────────┼─────────────────┼─────────────────┼─────────────┘ │
│           │                 │                 │                │
│  ┌────────▼─────────────────▼─────────────────▼─────────────┐ │
│  │              Business Logic Layer                         │ │
│  │                                                           │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │  Document    │  │   Gemini     │  │  Embedding   │  │ │
│  │  │  Processor   │  │   Agent      │  │   Service    │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │ │
│  │         │                  │                  │          │ │
│  │         └──────────────────┼──────────────────┘          │ │
│  │                            │                             │ │
│  │                    ┌───────▼────────┐                    │ │
│  │                    │  Graph Store   │                    │ │
│  │                    │   Manager      │                    │ │
│  │                    └───────┬────────┘                    │ │
│  └────────────────────────────┼───────────────────────────┘ │
└────────────────────────────────┼───────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
┌───────────────────▼────────┐   ┌───────────▼──────────────┐
│     Neo4j Database         │   │   Google Gemini API      │
│     (Port 7687/7474)       │   │   (External Service)     │
│                            │   │                          │
│  ┌──────────────────────┐ │   │  ┌────────────────────┐ │
│  │  Document Nodes      │ │   │  │  gemini-1.5-pro    │ │
│  │  - id                │ │   │  │  Model             │ │
│  │  - filename          │ │   │  └────────────────────┘ │
│  │  - metadata          │ │   │                          │
│  └──────────────────────┘ │   └──────────────────────────┘
│                            │
│  ┌──────────────────────┐ │
│  │  Chunk Nodes         │ │
│  │  - id                │ │
│  │  - content           │ │
│  │  - embedding (384d)  │ │
│  │  - metadata          │ │
│  └──────────────────────┘ │
│                            │
│  ┌──────────────────────┐ │
│  │  Relationships       │ │
│  │  - BELONGS_TO        │ │
│  │  - NEXT              │ │
│  └──────────────────────┘ │
└────────────────────────────┘
```

## Component Interaction Flow

### 1. Document Upload Flow

```
User Action: Upload Document
        │
        ▼
┌───────────────────┐
│  DocumentUpload   │
│   Component       │
└────────┬──────────┘
         │ POST /api/upload
         ▼
┌───────────────────┐
│  FastAPI Endpoint │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Document          │
│ Processor         │
│  - Extract Text   │
│  - Chunk Text     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Embedding         │
│ Service           │
│  - Generate       │
│    Embeddings     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Graph Store       │
│  - Store Document │
│  - Store Chunks   │
│  - Create Links   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Neo4j DB        │
│  - Save Nodes     │
│  - Save Relations │
└────────┬──────────┘
         │
         ▼
    Success Response
```

### 2. Chat Query Flow

```
User Action: Ask Question
        │
        ▼
┌───────────────────┐
│  ChatInterface    │
│   Component       │
└────────┬──────────┘
         │ POST /api/chat
         ▼
┌───────────────────┐
│  FastAPI Endpoint │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Embedding         │
│ Service           │
│  - Embed Query    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Graph Store       │
│  - Vector Search  │
│  - Get Top 5      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Neo4j DB        │
│  - Similarity     │
│    Search         │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Gemini Agent      │
│  - Format Context │
│  - Generate       │
│    Response       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Gemini API       │
│  - LLM Processing │
└────────┬──────────┘
         │
         ▼
    Response with Sources
```

## Data Models

### Document Node
```cypher
(:Document {
  id: String,
  filename: String,
  uploaded_at: DateTime,
  metadata: Map
})
```

### Chunk Node
```cypher
(:Chunk {
  id: String,
  content: String,
  chunk_index: Integer,
  embedding: List[Float],  // 384 dimensions
  metadata: Map
})
```

### Relationships
```cypher
(:Chunk)-[:BELONGS_TO]->(:Document)
(:Chunk)-[:NEXT {sequence: Integer}]->(:Chunk)
```

## API Endpoints

### Document Management
```
POST   /api/upload
GET    /api/documents
DELETE /api/documents/{id}
GET    /api/documents/{id}/chunks
```

### Chat
```
POST   /api/chat
```

### System
```
GET    /
GET    /health
```

## Technology Stack Details

### Backend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI | REST API, async support |
| Database | Neo4j 5.14 | Graph storage, vector search |
| Embeddings | Sentence Transformers | Local embedding generation |
| LLM | Google Gemini 1.5 Pro | Response generation |
| Text Processing | LangChain | Document chunking |
| PDF Processing | PyPDF | PDF text extraction |
| DOCX Processing | python-docx | Word document processing |
| Validation | Pydantic | Data validation |
| Server | Uvicorn | ASGI server |

### Frontend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18 | UI components |
| Build Tool | Vite | Fast dev server, bundling |
| Styling | TailwindCSS | Utility-first CSS |
| Icons | Lucide React | Icon library |
| HTTP Client | Axios | API requests |
| Markdown | React Markdown | Response formatting |
| File Upload | React Dropzone | Drag-and-drop upload |

## Security Architecture

```
┌─────────────────────────────────────────┐
│         Security Layers                 │
│                                         │
│  1. CORS Protection                     │
│     - Allowed origins only              │
│                                         │
│  2. File Validation                     │
│     - Type checking                     │
│     - Size limits                       │
│                                         │
│  3. Input Sanitization                  │
│     - Pydantic validation               │
│     - SQL injection prevention          │
│                                         │
│  4. API Key Management                  │
│     - Environment variables             │
│     - Never in code                     │
│                                         │
│  5. Database Security                   │
│     - Authentication required           │
│     - Connection encryption             │
│                                         │
│  6. Rate Limiting (TODO)                │
│     - Prevent abuse                     │
│                                         │
│  7. Authentication (TODO)               │
│     - User management                   │
│     - JWT tokens                        │
└─────────────────────────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- **Backend**: Multiple FastAPI instances behind load balancer
- **Frontend**: CDN distribution
- **Database**: Neo4j clustering

### Vertical Scaling
- **Increase resources** for embedding generation
- **More memory** for Neo4j caching
- **Faster storage** for document processing

### Optimization Points
1. **Caching Layer**: Redis for frequent queries
2. **Async Processing**: Celery for document processing
3. **Connection Pooling**: Neo4j driver optimization
4. **Batch Operations**: Process multiple documents
5. **CDN**: Static asset delivery

## Monitoring Architecture

```
┌─────────────────────────────────────────┐
│         Monitoring Stack                │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Application Metrics            │   │
│  │  - Request latency              │   │
│  │  - Error rates                  │   │
│  │  - Throughput                   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Database Metrics               │   │
│  │  - Query performance            │   │
│  │  - Connection pool              │   │
│  │  - Storage usage                │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  External API Metrics           │   │
│  │  - Gemini API latency           │   │
│  │  - API quota usage              │   │
│  │  - Error rates                  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Business Metrics               │   │
│  │  - Documents processed          │   │
│  │  - Queries per day              │   │
│  │  - User activity                │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Deployment Architecture

### Development
```
Local Machine
├── Backend (localhost:8000)
├── Frontend (localhost:3000)
└── Neo4j (localhost:7687)
```

### Production (Example)
```
Cloud Infrastructure
├── Frontend
│   └── Vercel/Netlify
├── Backend
│   ├── AWS ECS/Fargate
│   └── Load Balancer
├── Database
│   └── Neo4j Aura
└── Monitoring
    ├── CloudWatch
    └── Sentry
```

## Performance Benchmarks

### Expected Performance
- **Document Upload**: 2-5 seconds per MB
- **Embedding Generation**: 100-200 chunks/second
- **Vector Search**: <100ms for top-k=5
- **LLM Response**: 2-5 seconds
- **Total Query Time**: 3-6 seconds

### Optimization Targets
- **API Response**: <200ms (excluding LLM)
- **Vector Search**: <50ms
- **Document Processing**: <10 seconds for 10-page PDF
- **Frontend Load**: <1 second

---

This architecture is designed to be:
- **Scalable**: Can handle increasing load
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new features
- **Reliable**: Error handling and monitoring
- **Secure**: Multiple security layers
