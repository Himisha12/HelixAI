from typing import Dict, List
from fastapi import APIRouter
from app.services.prompt_service import PromptTemplate, prompt_service

router = APIRouter(prefix="/prompts", tags=["Prompt Engineering & Templates"])


@router.get(
    "",
    response_model=List[PromptTemplate],
    summary="List available prompt engineering templates"
)
async def list_prompt_templates() -> List[PromptTemplate]:
    return prompt_service.list_templates()


@router.post(
    "/{template_id}/render",
    summary="Render a prompt template with custom variables"
)
async def render_prompt_template(
    template_id: str, kwargs: Dict[str, str]
) -> Dict[str, str]:
    rendered = prompt_service.render_template(template_id, kwargs)
    return {"template_id": template_id, "rendered_prompt": rendered}
