from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends
from app.api.v1.auth import get_current_user
from app.core.rbac import Permission, PermissionChecker
from app.models.auth import UserInDB
from app.services.audit_service import AuditLogEntry, audit_logger

router = APIRouter(prefix="/audit-logs", tags=["Audit & Observability"])


@router.get(
    "",
    response_model=List[AuditLogEntry],
    summary="Retrieve system audit logs (RBAC Audit Read Required)"
)
async def get_audit_logs(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    tenant_id: Optional[str] = None,
    limit: int = 50,
) -> List[AuditLogEntry]:
    # Enforce RBAC Permission Guard
    PermissionChecker(Permission.AUDIT_READ)(current_user.role)
    return audit_logger.get_logs(tenant_id=tenant_id, limit=limit)
