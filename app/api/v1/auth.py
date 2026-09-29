from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.config import settings
from app.core.exceptions import AuthenticationException
from app.core.security import create_access_token, decode_access_token
from app.models.auth import Token, UserCreate, UserInDB, UserResponse
from app.services.auth_service import auth_service
from app.services.rate_limiter import rate_limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationException(detail="Invalid or expired JWT access token.")
    
    username: str = payload.get("sub", "")
    if not username:
        raise AuthenticationException(detail="Token payload missing subject.")
        
    user = auth_service.get_user_by_username(username)
    if not user:
        raise AuthenticationException(detail="User not found in system.")
        
    if not user.is_active:
        raise AuthenticationException(detail="User account is inactive.")
        
    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
async def register(user_in: UserCreate) -> UserResponse:
    try:
        return auth_service.register_user(user_in)
    except ValueError as e:
        raise AuthenticationException(detail=str(e))


@router.post(
    "/token",
    response_model=Token,
    summary="Obtain JWT access token via OAuth2 password flow"
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise AuthenticationException(detail="Incorrect username or password.")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    summary="Get current user profile and AI usage metrics"
)
async def get_me(current_user: Annotated[UserInDB, Depends(get_current_user)]):
    metrics = rate_limiter.get_usage_metrics(current_user.username)
    return {
        "user": UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            role=current_user.role,
            is_active=current_user.is_active,
        ),
        "usage_metrics": metrics,
    }
