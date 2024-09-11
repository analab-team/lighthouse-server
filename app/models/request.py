from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Request(BaseModel):
    request_id: UUID = Field(default_factory=lambda: str(uuid4()))
    product_id: UUID
    user_id: str
    input_text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class RequestResult(BaseModel):
    result_id: UUID = Field(default_factory=lambda: uuid4())
    request_id: UUID
    analyzer_name: str
    metric: float
    reject_flg: bool
