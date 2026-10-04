import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    id: str = Field(default_factory=lambda: "audit-" + str(uuid.uuid4())[:8])
    timestamp: str = Field(
        default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    )
    user_id: str
    tenant_id: str = "tenant-default"
    action: str
    resource: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)


class AuditLogger:
    """
    Enterprise Structured Audit Logger tracking all security-relevant actions,
    authorization guards, LLM inference calls, and tool executions.
    """

    def __init__(self) -> None:
        self._logs: List[AuditLogEntry] = []

    def log(
        self,
        user_id: str,
        action: str,
        resource: str,
        status: str = "SUCCESS",
        tenant_id: str = "tenant-default",
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource=resource,
            status=status,
            details=details or {},
        )
        self._logs.insert(0, entry)  # Prepend newest logs first
        # Limit memory history to 500 entries
        if len(self._logs) > 500:
            self._logs = self._logs[:500]
        return entry

    def get_logs(
        self, tenant_id: Optional[str] = None, user_id: Optional[str] = None, limit: int = 50
    ) -> List[AuditLogEntry]:
        results = self._logs
        if tenant_id:
            results = [log for log in results if log.tenant_id == tenant_id]
        if user_id:
            results = [log for log in results if log.user_id == user_id]
        return results[:limit]


# Global singleton Audit Logger
audit_logger = AuditLogger()
