from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Response(BaseModel):
    response_id: UUID = Field(default_factory=lambda: uuid4())
    request_id: UUID
    output_text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
