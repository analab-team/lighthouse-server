from typing import Dict, List

from pydantic import BaseModel


class GetAnalyzersResponse(BaseModel):
    input: List[str]
    output: List[str]


class AddAnalyzerRequest(BaseModel):
    analyzer_name: str
    vault: dict


class GetVaultExample(BaseModel):
    fields: Dict[str, str]
