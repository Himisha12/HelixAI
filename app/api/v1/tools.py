from typing import Annotated, List
from fastapi import APIRouter, Depends
from app.api.v1.auth import get_current_user
from app.core.rbac import Permission, PermissionChecker
from app.models.auth import UserInDB
from app.models.tools import ToolDefinition, ToolExecutionRequest, ToolExecutionResponse
from app.services.audit_service import audit_logger
from app.services.tool_service import tool_service

router = APIRouter(prefix="/tools", tags=["LLM Tools & Execution"])


@router.get(
    "",
    response_model=List[ToolDefinition],
    summary="List available AI tools in system registry"
)
async def list_tools() -> List[ToolDefinition]:
    return tool_service.list_tools()


@router.post(
    "/execute",
    response_model=ToolExecutionResponse,
    summary="Safely execute an LLM tool call (JWT Protected & RBAC Guarded)"
)
async def execute_tool(
    request: ToolExecutionRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> ToolExecutionResponse:
    # Enforce RBAC Permission Guard
    PermissionChecker(Permission.TOOLS_EXECUTE)(current_user.role)

    response = tool_service.execute_tool(request)

    # Log Security Audit Record
    audit_logger.log(
        user_id=current_user.username,
        action="TOOL_EXECUTION",
        resource=f"/tools/execute?name={request.tool_name}",
        status=response.status.upper(),
        details={"tool_name": request.tool_name, "arguments": request.arguments},
    )

    return response
