from uuid import UUID

from pydantic import BaseModel, field_validator


class MonitoringInputRequest(BaseModel):
    user_id: str
    input_text: str


class MonitoringInputResponse(BaseModel):
    mode: str
    request_id: UUID

    @field_validator("request_id", mode="before")
    def transform_id_to_str(cls, value) -> UUID:
        return UUID(value)


class MonitoringOutputRequest(BaseModel):
    request_id: UUID
    output_text: str


class MonitoringOutputResponse(BaseModel):
    reject_flg: bool | None


class ChangeModeRequest(BaseModel):
    mode: str
