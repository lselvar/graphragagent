# GraphRAG Agent

A full-stack application that combines **Graph RAG (Retrieval-Augmented Generation)** with **Google's Gemini LLM** to provide intelligent document querying capabilities. The application uses Neo4j for graph-based storage of document embeddings and features a modern React frontend.

## 🌟 Features

- **Document Upload**: Support for PDF, DOCX, and TXT files
- **Graph-Based Storage**: Neo4j graph database for storing document embeddings and relationships
- **Vector Search**: Efficient similarity search using vector embeddings
- **Gemini LLM Integration**: Powered by Google's Gemini 1.5 Pro model
- **Interactive Chat Interface**: Modern UI for querying documents
- **Document Management**: View and manage uploaded documents
- **Source Attribution**: Responses include relevant source documents

## 🏗️ Architecture

### Backend (Python + FastAPI)
- **FastAPI**: High-performance REST API
- **Neo4j**: Graph database for storing embeddings and relationships
- **Sentence Transformers**: Local embedding generation
- **Google Gemini**: LLM for response generation
- **LangChain**: Text processing and chunking

### Frontend (React + Vite)
- **React 18**: Modern UI framework
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first styling
- **Lucide Icons**: Beautiful icon set
- **React Markdown**: Formatted response rendering

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Docker and Docker Compose (for Neo4j)
- Google API Key (for Gemini)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd graphragagent
```

### 2. Set Up Neo4j Database

Start Neo4j using Docker Compose:

```bash
docker-compose up -d
```

Access Neo4j Browser at `http://localhost:7474` (username: `neo4j`, password: `password123`)

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
GOOGLE_API_KEY=your_google_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

### 4. Install Backend Dependencies

Using Poetry (recommended):

```bash
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
```

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## 🎯 Running the Application

### Start the Backend

From the root directory:

```bash
# Using Poetry
poetry run python -m backend.main

# Or using Python directly
python -m backend.main
```

The backend API will be available at `http://localhost:8000`

### Start the Frontend

In a new terminal, from the `frontend` directory:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 Usage

### 1. Upload Documents

- Navigate to the **Upload** tab
- Drag and drop or click to select a document (PDF, DOCX, or TXT)
- Wait for the document to be processed and chunked
- The system will automatically generate embeddings and store them in Neo4j

### 2. Query Documents

- Navigate to the **Chat** tab
- Type your question in the input field
- The system will:
  - Generate an embedding for your query
  - Search for relevant document chunks using vector similarity
  - Use Gemini LLM to generate a contextual response
  - Display the response with source attribution

### 3. Manage Documents

- Navigate to the **Documents** tab
- View all uploaded documents
- Delete documents as needed

## 🔧 API Endpoints

### Document Management

- `POST /api/upload` - Upload a document
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{document_id}` - Delete a document
- `GET /api/documents/{document_id}/chunks` - Get document chunks

### Chat

- `POST /api/chat` - Send a chat message and get a response

### Health

- `GET /health` - Health check endpoint
- `GET /` - API information

## 🛠️ Configuration

### Backend Configuration

Edit `backend/config.py` or use environment variables:

- `GOOGLE_API_KEY`: Your Google API key for Gemini
- `NEO4J_URI`: Neo4j connection URI
- `NEO4J_USER`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password
- `EMBEDDING_MODEL`: Sentence transformer model name
- `CHUNK_SIZE`: Text chunk size (default: 1000)
- `CHUNK_OVERLAP`: Chunk overlap size (default: 200)
- `GEMINI_MODEL`: Gemini model name (default: gemini-1.5-pro)
- `TEMPERATURE`: LLM temperature (default: 0.7)
- `MAX_TOKENS`: Maximum response tokens (default: 2048)

### Frontend Configuration

Create `frontend/.env.local` for custom API URL:

```env
VITE_API_URL=http://localhost:8000
```

## 📦 Project Structure

```
graphragagent/
├── backend/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── main.py                # FastAPI application
│   ├── models.py              # Pydantic models
│   ├── graph_store.py         # Neo4j graph operations
│   ├── embeddings.py          # Embedding generation
│   ├── document_processor.py  # Document processing
│   └── gemini_agent.py        # Gemini LLM integration
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js      # API client
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   └── DocumentList.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── pyproject.toml             # Poetry dependencies
├── docker-compose.yml         # Neo4j setup
├── .env.example               # Environment template
└── README.md
```

## 🧪 Development

### Backend Development

```bash
# Run with auto-reload
poetry run uvicorn backend.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black backend/

# Type checking
poetry run mypy backend/
```

### Frontend Development

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🐛 Troubleshooting

### Neo4j Connection Issues

- Ensure Neo4j is running: `docker-compose ps`
- Check Neo4j logs: `docker-compose logs neo4j`
- Verify credentials in `.env` file

### Embedding Model Download

On first run, the sentence transformer model will be downloaded automatically. This may take a few minutes.

### API Key Issues

- Ensure your Google API key is valid and has Gemini API access
- Check the key is correctly set in the `.env` file

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.
