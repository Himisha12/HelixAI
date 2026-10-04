from datetime import timedelta
from typing import Annotated, Any, Dict, List
from fastapi import APIRouter, Depends, Header, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.config import settings
from app.core.exceptions import AuthenticationException
from app.core.rbac import Permission, PermissionChecker
from app.core.security import create_access_token, decode_access_token
from app.models.auth import Token, UserCreate, UserInDB, UserResponse
from app.services.audit_service import audit_logger
from app.services.auth_service import auth_service
from app.services.rate_limiter import rate_limiter

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    x_tenant_id: Annotated[str, Header()] = "tenant-default",
) -> UserInDB:
    payload = decode_access_token(token)
    if not payload:
        audit_logger.log("anonymous", "JWT_DECODE_FAILED", "/auth/me", "FAILURE", x_tenant_id)
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
async def register(
    user_in: UserCreate,
    x_tenant_id: Annotated[str, Header()] = "tenant-default",
) -> UserResponse:
    try:
        user_res = auth_service.register_user(user_in)
        audit_logger.log(user_res.username, "USER_REGISTER", f"/auth/users/{user_res.id}", "SUCCESS", x_tenant_id)
        return user_res
    except ValueError as e:
        audit_logger.log(user_in.username, "USER_REGISTER_FAILED", "/auth/register", "FAILURE", x_tenant_id, {"error": str(e)})
        raise AuthenticationException(detail=str(e))


@router.post(
    "/token",
    response_model=Token,
    summary="Obtain JWT access token via OAuth2 password flow"
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    x_tenant_id: Annotated[str, Header()] = "tenant-default",
) -> Token:
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        audit_logger.log(form_data.username, "USER_LOGIN_FAILED", "/auth/token", "FAILURE", x_tenant_id)
        raise AuthenticationException(detail="Incorrect username or password.")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "tenant_id": x_tenant_id},
        expires_delta=access_token_expires,
    )
    audit_logger.log(user.username, "USER_LOGIN_SUCCESS", "/auth/token", "SUCCESS", x_tenant_id, {"role": user.role})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    summary="Get current user profile, RBAC permissions, and AI usage metrics"
)
async def get_me(current_user: Annotated[UserInDB, Depends(get_current_user)]) -> Dict[str, Any]:
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


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all registered system users (RBAC Admin Required)"
)
async def list_users(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> List[UserResponse]:
    PermissionChecker(Permission.ADMIN_ALL)(current_user.role)
    return auth_service.list_users()
