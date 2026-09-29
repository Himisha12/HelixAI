from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid user email address")
    role: str = Field(default="user", description="User role (user, admin)")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Raw password minimum 6 characters")


class UserResponse(UserBase):
    id: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    id: str
    hashed_password: str
    is_active: bool = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = "user"
