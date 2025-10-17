# Google Agent Development Kit (ADK) Integration

## Overview

The GraphRAG Agent now uses **Google's Agent Development Kit (ADK)** with **Gemini 2.0 Flash** model for enhanced AI capabilities.

## What Changed

### 1. Updated Dependencies

**pyproject.toml**:
- Added `google-genai` for ADK support
- Added `google-generativeai` for compatibility
- Updated to support latest Gemini models

### 2. New Gemini Model

**Gemini 2.0 Flash Experimental**:
- Model: `gemini-2.0-flash-exp`
- Faster response times
- Improved context understanding
- Better instruction following
- Increased token limit: 8,192 tokens (up from 2,048)

### 3. ADK Agent Implementation

**backend/gemini_agent.py**:
```python
from google import genai
from google.genai import types

class GeminiAgent:
    """Gemini LLM agent using Google Agent Development Kit (ADK)."""
    
    def __init__(self):
        # Initialize ADK client
        self.client = genai.Client(api_key=settings.google_api_key)
        
        # Configure agent with system instructions
        self.agent_config = types.GenerateContentConfig(
            temperature=settings.temperature,
            max_output_tokens=settings.max_tokens,
            system_instruction="..."
        )
```

## Key Features

### 1. System Instructions
The agent now has built-in system instructions that define its behavior:
- Specialized in document-based Q&A
- Analyzes context carefully
- Provides accurate, well-structured responses
- Cites sources when relevant
- Maintains conversation context

### 2. Structured Message Format
Uses ADK's `Content` and `Part` types for better message handling:
```python
types.Content(
    role="user",
    parts=[types.Part(text=message)]
)
```

### 3. Conversation History
Properly maintains conversation context across multiple interactions using ADK's message format.

### 4. Enhanced Error Handling
Better error messages and logging for ADK-specific issues.

## Benefits of ADK

### 1. **Better Agent Capabilities**
- System-level instructions for consistent behavior
- Improved context management
- Better multi-turn conversations

### 2. **Modern API**
- Type-safe with Pydantic models
- Cleaner, more maintainable code
- Better IDE support

### 3. **Performance**
- Gemini 2.0 Flash is faster than 1.5 Pro
- Lower latency for responses
- More efficient token usage

### 4. **Future-Proof**
- ADK is Google's recommended approach
- Access to latest Gemini features
- Regular updates and improvements

## Configuration

### Environment Variables

Update your `.env` file:

```env
# Google API Key (required)
GOOGLE_API_KEY=your_api_key_here

# Model Configuration
GEMINI_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.7
MAX_TOKENS=8192
```

### Available Models

You can switch between models by changing `GEMINI_MODEL`:

- `gemini-2.0-flash-exp` - Latest experimental (recommended)
- `gemini-1.5-pro` - Stable, high-quality
- `gemini-1.5-flash` - Fast, efficient

## Usage

The API remains the same from the application perspective:

```python
# Generate response
response = await gemini_agent.generate_response(
    query="What is this document about?",
    retrieved_chunks=chunks,
    conversation_history=history
)

# Generate summary
summary = await gemini_agent.generate_summary(text)

# Extract entities
entities = await gemini_agent.extract_entities(text)
```

## Installation

### 1. Update Dependencies

```bash
poetry install
```

This will install:
- `google-genai` - ADK library
- `google-generativeai` - Supporting library

### 2. Restart Backend

```bash
poetry run python -m backend.main
```

## Testing

### Test ADK Integration

```python
from backend.gemini_agent import GeminiAgent
from backend.config import settings

# Initialize agent
agent = GeminiAgent()

# Test simple query
response = await agent.generate_response(
    query="Hello, how are you?",
    retrieved_chunks=[]
)

print(response)
```

### Test with Documents

1. Upload a document through the UI
2. Ask questions in the chat
3. Verify responses are accurate and well-formatted

## Troubleshooting

### "Module not found: google.genai"

```bash
# Reinstall dependencies
poetry install --no-cache
```

### "API key not valid"

- Verify your Google API key in `.env`
- Ensure the key has Gemini API access
- Check for typos or extra spaces

### "Model not found: gemini-2.0-flash-exp"

If the experimental model is not available:

```env
# Use stable version instead
GEMINI_MODEL=gemini-1.5-pro
```

### Rate Limiting

If you hit rate limits:
- Reduce request frequency
- Use `gemini-1.5-flash` for higher quotas
- Upgrade your Google Cloud quota

## Migration from Old Implementation

### What Stayed the Same
- ✅ API interface (no changes to calling code)
- ✅ Response format
- ✅ Error handling patterns
- ✅ Async/await support

### What Changed
- ✅ Internal implementation uses ADK
- ✅ Better system instructions
- ✅ Improved message formatting
- ✅ Enhanced conversation history

### No Breaking Changes
The migration is **backward compatible**. Your existing code will continue to work without modifications.

## Performance Comparison

| Metric | Gemini 1.5 Pro | Gemini 2.0 Flash |
|--------|----------------|------------------|
| **Response Time** | 3-5 seconds | 1-3 seconds |
| **Max Tokens** | 2,048 | 8,192 |
| **Context Window** | 128K | 1M |
| **Quality** | Excellent | Very Good |
| **Cost** | Higher | Lower |

## Advanced Features

### Custom System Instructions

Modify the system instruction in `backend/gemini_agent.py`:

```python
self.agent_config = types.GenerateContentConfig(
    temperature=settings.temperature,
    max_output_tokens=settings.max_tokens,
    system_instruction="Your custom instructions here..."
)
```

### Adjust Temperature

Control creativity vs. consistency:

```env
# More creative (0.0 - 1.0)
TEMPERATURE=0.9

# More consistent
TEMPERATURE=0.3
```

### Increase Token Limit

For longer responses:

```env
# Up to 8,192 for Gemini 2.0 Flash
MAX_TOKENS=8192
```

## Best Practices

### 1. **System Instructions**
- Keep them clear and specific
- Define expected behavior
- Include constraints and guidelines

### 2. **Context Management**
- Limit conversation history to last 5 messages
- Include only relevant document chunks
- Format context clearly

### 3. **Error Handling**
- Always catch and log exceptions
- Provide fallback responses
- Monitor API errors

### 4. **Performance**
- Use Gemini 2.0 Flash for speed
- Cache frequent queries
- Batch similar requests

## Resources

- [Google ADK Documentation](https://ai.google.dev/adk)
- [Gemini API Reference](https://ai.google.dev/api)
- [Gemini Models Overview](https://ai.google.dev/models/gemini)
- [Best Practices Guide](https://ai.google.dev/docs/best_practices)

## Support

For issues related to:
- **ADK Integration**: Check this documentation
- **API Errors**: Review Google Cloud Console
- **Model Availability**: Check Gemini API status

---

**Status**: ✅ Fully Integrated and Tested  
**Version**: 0.2.0  
**Date**: October 15, 2025  
**Model**: Gemini 2.0 Flash Experimental
