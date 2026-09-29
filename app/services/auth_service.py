import uuid
from typing import Dict, Optional
from app.core.security import hash_password, verify_password
from app.models.auth import UserCreate, UserInDB, UserResponse


class AuthService:
    """
    In-memory User Management & Authentication Service.
    In a full production database setup, this connects to PostgreSQL/MongoDB via SQLAlchemy/Beanie.
    """

    def __init__(self) -> None:
        self._users_db: Dict[str, UserInDB] = {}
        # Pre-seed demo user for testing & video demo convenience
        self._seed_demo_user()

    def _seed_demo_user(self) -> None:
        demo_id = "user-" + str(uuid.uuid4())[:8]
        demo_user = UserInDB(
            id=demo_id,
            username="demo_user",
            email="demo@ai-microservice.io",
            role="user",
            hashed_password=hash_password("demo123"),
            is_active=True,
        )
        self._users_db["demo_user"] = demo_user

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        return self._users_db.get(username)

    def register_user(self, user_create: UserCreate) -> UserResponse:
        if user_create.username in self._users_db:
            raise ValueError(f"Username '{user_create.username}' is already registered.")

        user_id = "user-" + str(uuid.uuid4())[:8]
        hashed_pwd = hash_password(user_create.password)

        user_in_db = UserInDB(
            id=user_id,
            username=user_create.username,
            email=user_create.email,
            role=user_create.role,
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
