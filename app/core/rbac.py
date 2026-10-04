from enum import Enum
from typing import Dict, Set
from app.core.exceptions import PermissionDeniedException


class Role(str, Enum):
    ADMIN = "admin"
    DATA_ENGINEER = "data_engineer"
    ANALYST = "analyst"
    USER = "user"


class Permission(str, Enum):
    CHAT_INFER = "chat:infer"
    TOOLS_EXECUTE = "tools:execute"
    METRICS_READ = "metrics:read"
    MODELS_READ = "models:read"
    ADMIN_ALL = "admin:all"
    POLICY_EVALUATE = "policy:evaluate"


# Role to Permissions Mapping (Principle of Least Privilege)
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.CHAT_INFER,
        Permission.TOOLS_EXECUTE,
        Permission.METRICS_READ,
        Permission.MODELS_READ,
        Permission.ADMIN_ALL,
        Permission.POLICY_EVALUATE,
    },
    Role.DATA_ENGINEER: {
        Permission.CHAT_INFER,
        Permission.TOOLS_EXECUTE,
        Permission.METRICS_READ,
        Permission.MODELS_READ,
        Permission.POLICY_EVALUATE,
    },
    Role.ANALYST: {
        Permission.CHAT_INFER,
        Permission.TOOLS_EXECUTE,
        Permission.METRICS_READ,
        Permission.MODELS_READ,
    },
    Role.USER: {
        Permission.CHAT_INFER,
        Permission.TOOLS_EXECUTE,
        Permission.MODELS_READ,
    },
}


class PermissionChecker:
    """
    FastAPI Security Dependency Guard enforcing Role-Based Access Control (RBAC).
    Verifies if the current authenticated user's role grants the required permission.
    """

    def __init__(self, required_permission: Permission) -> None:
        self.required_permission = required_permission

    def __call__(self, user_role: str) -> bool:
        try:
            role_enum = Role(user_role.lower())
        except ValueError:
            raise PermissionDeniedException(detail=f"Invalid or unrecognized user role: '{user_role}'.")

        allowed_permissions = ROLE_PERMISSIONS.get(role_enum, set())
        if Permission.ADMIN_ALL in allowed_permissions:
            return True

        if self.required_permission not in allowed_permissions:
            raise PermissionDeniedException(
                detail=(
                    f"Permission denied. Role '{user_role}' lacks required permission "
                    f"'{self.required_permission.value}'."
                )
            )

        return True
