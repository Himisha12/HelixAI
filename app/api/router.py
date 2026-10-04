from fastapi import APIRouter
from app.api.v1.agent import router as agent_router
from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.models import router as models_router
from app.api.v1.prompts import router as prompts_router
from app.api.v1.tools import router as tools_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(agent_router)
api_router.include_router(tools_router)
api_router.include_router(prompts_router)
api_router.include_router(models_router)
api_router.include_router(audit_router)
