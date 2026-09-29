from typing import List
from fastapi import APIRouter
from app.models.chat import ModelInfo
from app.services.llm_service import llm_service

router = APIRouter(prefix="/models", tags=["Open Models Registry"])


@router.get(
    "",
    response_model=List[ModelInfo],
    summary="List available open models and execution backend states"
)
async def list_models() -> List[ModelInfo]:
    return llm_service.list_models()
