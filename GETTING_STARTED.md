# Getting Started with GraphRAG Agent

## What You Need

Before starting, make sure you have:

1. **Google API Key** - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Docker** - For running Neo4j database
3. **Python 3.10+** - For the backend
4. **Node.js 18+** - For the frontend

## Installation Steps

### Step 1: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file and add your Google API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
NEO4J_PASSWORD=password123
```

### Step 2: Start Neo4j Database

```bash
docker-compose up -d
```

This will start Neo4j on:
- Bolt: `bolt://localhost:7687`
- HTTP: `http://localhost:7474`

### Step 3: Install Python Dependencies

```bash
poetry install
```

If you don't have Poetry, install it first:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Step 4: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 5: Start the Application

**Terminal 1 - Backend:**
```bash
poetry run python -m backend.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Using the Application

### 1. Upload Documents

1. Open http://localhost:3000
2. Click on the **Upload** tab
3. Drag and drop a document (PDF, DOCX, or TXT)
4. Wait for processing to complete

The system will:
- Extract text from your document
- Split it into chunks
- Generate embeddings using Sentence Transformers
- Store everything in Neo4j graph database

### 2. Chat with Your Documents

1. Click on the **Chat** tab
2. Type your question
3. Press Send or hit Enter

The system will:
- Convert your question to an embedding
- Search for relevant chunks in the graph
- Use Gemini LLM to generate a contextual answer
- Show you the sources used

### 3. Manage Documents

1. Click on the **Documents** tab
2. View all uploaded documents
3. Delete documents you no longer need

## Example Workflow

1. **Upload a research paper** (PDF)
   - The system chunks it into ~1000 character segments
   - Creates embeddings for each chunk
   - Stores them in Neo4j with relationships

2. **Ask questions like:**
   - "What is the main conclusion of this paper?"
   - "Explain the methodology used"
   - "What are the key findings?"

3. **Get AI-powered answers** with source attribution

## Architecture Overview

```
┌─────────────┐
│   React UI  │  (Port 3000)
└──────┬──────┘
       │
       │ HTTP/REST
       │
┌──────▼──────┐
│  FastAPI    │  (Port 8000)
│  Backend    │
└──────┬──────┘
       │
       ├─────────────┐
       │             │
┌──────▼──────┐ ┌───▼────────┐
│   Neo4j     │ │   Gemini   │
│  (GraphDB)  │ │    LLM     │
└─────────────┘ └────────────┘
```

## Key Features

### Graph RAG
- **Graph-based storage** of document chunks
- **Vector similarity search** for retrieval
- **Relationship tracking** between chunks
- **Efficient querying** with Neo4j

### Gemini Integration
- **Google's Gemini 1.5 Pro** model
- **Context-aware responses**
- **Conversation history** support
- **Source attribution**

### Modern UI
- **React 18** with Vite
- **TailwindCSS** styling
- **Responsive design**
- **Real-time updates**

## Configuration Options

Edit `backend/config.py` or `.env` to customize:

```python
# Embedding settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# LLM settings
GEMINI_MODEL = "gemini-1.5-pro"
TEMPERATURE = 0.7
MAX_TOKENS = 2048
```

## Troubleshooting

### Backend won't start
- Check if Neo4j is running: `docker ps`
- Verify `.env` file exists and has correct values
- Ensure Python dependencies are installed: `poetry install`

### Frontend won't start
- Check if backend is running on port 8000
- Verify Node modules are installed: `cd frontend && npm install`
- Clear cache: `rm -rf frontend/node_modules frontend/.vite`

### No search results
- Make sure you've uploaded documents first
- Check Neo4j is running and accessible
- Verify embeddings were created (check backend logs)

### Gemini API errors
- Verify your API key is valid
- Check you have Gemini API access enabled
- Ensure you're not hitting rate limits

## Next Steps

1. **Try different document types** - PDFs, Word docs, text files
2. **Experiment with queries** - Ask complex questions
3. **Upload multiple documents** - Build a knowledge base
4. **Customize the UI** - Modify React components
5. **Adjust chunking** - Optimize for your use case

## Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Google Gemini API](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## Support

For issues or questions:
1. Check the [README.md](README.md) for detailed documentation
2. Review the [SETUP.md](SETUP.md) for installation help
3. Open an issue on GitHub

Happy querying! 🚀
