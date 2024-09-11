from pydantic import BaseModel


class AddAnalyzerRequest(BaseModel):
    analyzer_name: str
    description: str
    host: str
    port: int
    endpoint: str
    type: str


class AddProductResponse(BaseModel):
    api_key: str
