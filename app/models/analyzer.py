from urllib.parse import urlparse

from pydantic import BaseModel, field_validator


class Analyzer(BaseModel):
    analyzer_name: str
    description: str
    host: str
    port: int
    endpoint: str
    type: str

    @field_validator("host")
    def validate_endpoint(cls, v):
        result = urlparse(v)
        assert len(result.scheme) > 0 and len(result.netloc) > 0
        return v

    @field_validator("type")
    def validate_type(cls, v):
        assert v in ["input", "output"]
        return v
