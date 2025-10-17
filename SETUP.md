# Quick Setup Guide

## Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Docker and Docker Compose installed
- [ ] Google API Key with Gemini access

## Quick Start (5 minutes)

### 1. Get Your Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_actual_key_here
```

### 3. Start Everything

```bash
# Make the startup script executable
chmod +x start.sh

# Run the startup script
./start.sh
```

That's it! The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Neo4j Browser: http://localhost:7474

## Manual Setup

If you prefer to start services individually:

### 1. Start Neo4j

```bash
docker-compose up -d
```

### 2. Install Backend Dependencies

```bash
poetry install
```

### 3. Start Backend

```bash
poetry run python -m backend.main
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Start Frontend

```bash
npm run dev
```

## Verify Installation

1. Open http://localhost:3000
2. Navigate to the Upload tab
3. Upload a test document (PDF, DOCX, or TXT)
4. Go to the Chat tab
5. Ask a question about your document

## Common Issues

### "Neo4j connection failed"

- Check if Docker is running: `docker ps`
- Restart Neo4j: `docker-compose restart`

### "Google API key invalid"

- Verify your key in the `.env` file
- Ensure the key has Gemini API access enabled

### "Module not found" errors

- Backend: Run `poetry install`
- Frontend: Run `cd frontend && npm install`

## Next Steps

1. Upload your documents in the Upload tab
2. Start chatting with your documents in the Chat tab
3. Manage your documents in the Documents tab

For more details, see the main [README.md](README.md).
