from __future__ import annotations

from fastapi import APIRouter

from .analyze_crud import perform_analysis
from .analyze_schema import AnalyzeRequest, AnalyzeResponse

router = APIRouter(prefix="/analyze", tags=["Analyze"])


@router.post("", response_model=AnalyzeResponse)
def analyze_endpoint(payload: AnalyzeRequest):
    return perform_analysis(payload)
