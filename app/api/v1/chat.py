from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.v1.auth import get_current_user
from app.core.rbac import Permission, PermissionChecker
from app.models.auth import UserInDB
from app.models.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.llm_service import llm_service
from app.services.rate_limiter import rate_limiter

router = APIRouter(prefix="/chat", tags=["AI Chat Completions"])


@router.post(
    "/completions",
    response_model=ChatCompletionResponse,
    summary="Generate open LLM model chat completion (JWT Protected, Rate Limited)"
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> ChatCompletionResponse:
    # 1. Enforce RBAC Permission Guard
    PermissionChecker(Permission.CHAT_INFER)(current_user.role)

    # 2. Enforce AI Rate Limiting (RPM and TPM)
    estimated_prompt_tokens = llm_service._estimate_tokens(
        " ".join([m.content for m in request.messages])
    )
    rate_limiter.check_rate_limit(
        user_id=current_user.username, estimated_tokens=estimated_prompt_tokens
    )

    # 3. Execute Model Inference Boundary Call
    response = await llm_service.generate_completion(request)

    # 4. Record Actual Usage in Sliding Window Rate Limiter
    rate_limiter.record_usage(
        user_id=current_user.username, actual_tokens=response.usage.total_tokens
    )

    return response
