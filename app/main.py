from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "Production Containerized FastAPI Microservice running Open Models locally or via free-tier API. "
        "Protected by JWT Authentication, Pydantic v2 validation, AI Rate Limiting, and LLM Tool Calling."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend access (Streamlit, React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Versioned API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health Check"], summary="Check Microservice Health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "llm_backend": settings.LLM_BACKEND,
        "default_model": settings.DEFAULT_MODEL,
    }


@app.get("/", tags=["Root"], summary="Microservice Root Overview")
async def root() -> Dict[str, Any]:
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "health_check": "/health",
        "api_v1": settings.API_V1_STR,
    }
