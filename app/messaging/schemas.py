from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentUploadedEvent(BaseModel):
    """Message published by rag-assistant-api after a successful upload."""

    event_id: UUID
    document_id: UUID
    file_path: str
    timestamp: datetime