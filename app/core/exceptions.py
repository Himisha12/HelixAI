from fastapi import HTTPException, status


class RateLimitExceededException(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded. Please try again later.") -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "60"},
        )


class AuthenticationException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ModelExecutionException(HTTPException):
    def __init__(self, detail: str = "Error occurred during model execution") -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )


class ToolExecutionException(HTTPException):
    def __init__(self, detail: str = "Error occurred during tool execution") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
