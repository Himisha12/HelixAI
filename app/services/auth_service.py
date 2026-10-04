import uuid
from typing import Dict, List, Optional
from app.core.rbac import Role
from app.core.security import hash_password, verify_password
from app.models.auth import UserCreate, UserInDB, UserResponse


class AuthService:
    """
    In-memory User Management & Authentication Service.
    In a full production database setup, this connects to PostgreSQL/MongoDB via SQLAlchemy/Beanie.
    Pre-seeded with RBAC demo accounts (Admin, Auditor, Developer, User).
    """

    def __init__(self) -> None:
        self._users_db: Dict[str, UserInDB] = {}
        # Pre-seed demo users across all roles for RBAC testing & Loom video demo
        self._seed_demo_users()

    def _seed_demo_users(self) -> None:
        demo_accounts = [
            ("demo_user", "demo@ai-microservice.io", "demo123", Role.USER.value),
            ("admin_user", "admin@ai-microservice.io", "admin123", Role.ADMIN.value),
            ("auditor_user", "auditor@ai-microservice.io", "audit123", Role.AUDITOR.value),
            ("dev_user", "dev@ai-microservice.io", "dev123", Role.DEVELOPER.value),
        ]

        for username, email, pwd, role in demo_accounts:
            user_id = f"user-{username[:5]}-" + str(uuid.uuid4())[:6]
            self._users_db[username] = UserInDB(
                id=user_id,
                username=username,
                email=email,
                role=role,
                hashed_password=hash_password(pwd),
                is_active=True,
            )

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        return self._users_db.get(username)

    def list_users(self) -> List[UserResponse]:
        return [
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
            )
            for u in self._users_db.values()
        ]

    def register_user(self, user_create: UserCreate) -> UserResponse:
        if user_create.username in self._users_db:
            raise ValueError(f"Username '{user_create.username}' is already registered.")

        user_id = "user-" + str(uuid.uuid4())[:8]
        hashed_pwd = hash_password(user_create.password)

        user_in_db = UserInDB(
            id=user_id,
            username=user_create.username,
            email=user_create.email,
            role=user_create.role or Role.USER.value,
            hashed_password=hashed_pwd,
            is_active=True,
        )

        self._users_db[user_create.username] = user_in_db

        return UserResponse(
            id=user_in_db.id,
            username=user_in_db.username,
            email=user_in_db.email,
            role=user_in_db.role,
            is_active=user_in_db.is_active,
        )

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


# Global singleton instance
auth_service = AuthService()
