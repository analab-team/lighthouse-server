from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class AnalyzerResult(BaseModel):
    timestamp: datetime
    text: str
    metric: float
    reject_flg: bool
    reasons: str


class AnalysisResults(BaseModel):
    input: Dict[str, List[AnalyzerResult]]
    output: Dict[str, List[AnalyzerResult]]
