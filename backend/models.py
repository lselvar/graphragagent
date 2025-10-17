from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentUpload(BaseModel):
    """Model for document upload response."""
    id: str
    filename: str
    size: int
    uploaded_at: datetime
    chunks_created: int
    status: str


class ChatMessage(BaseModel):
    """Model for chat messages."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Model for chat query request."""
    message: str = Field(..., description="User's question")
    conversation_history: Optional[List[ChatMessage]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Model for chat query response."""
    response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime


class DocumentChunk(BaseModel):
    """Model for document chunks stored in graph."""
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphNode(BaseModel):
    """Model for graph nodes."""
    id: str
    type: str
    properties: Dict[str, Any]


class GraphRelationship(BaseModel):
    """Model for graph relationships."""
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
