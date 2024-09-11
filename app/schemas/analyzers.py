from uuid import UUID

from pydantic import BaseModel, field_serializer


class InputRequest(BaseModel):
    request_id: UUID
    input_text: str
    analyzer_name: str

    @field_serializer("request_id")
    def transform_id_to_str(value) -> str:
        return str(value)


class OutputRequest(BaseModel):
    response_id: UUID
    output_text: str
    analyzer_name: str

    @field_serializer("response_id")
    def transform_id_to_str(value) -> str:
        return str(value)


class OutputResponse(BaseModel):
    reject_flg: bool
