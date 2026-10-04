import time
from typing import Annotated, Any, Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.api.v1.auth import get_current_user
from app.core.rbac import Permission, PermissionChecker
from app.models.auth import UserInDB
from app.models.chat import ChatCompletionRequest, ChatMessage
from app.models.tools import ToolExecutionRequest
from app.services.llm_service import llm_service
from app.services.tool_service import tool_service

router = APIRouter(prefix="/agent", tags=["AI Data Analyst & Web Researcher Agent"])


class AgentRunRequest(BaseModel):
    task_description: str = Field(
        ...,
        description="Goal prompt for the AI Data Analyst & Web Researcher Agent",
        json_schema_extra={"example": "Generate top revenue customer SQL query in Snowflake and research cloud data warehouse indexing best practices."},
    )
    model: str = Field(default="llama3-open-8b")
    document_payload: str = Field(
        default="",
        description="Optional uploaded CSV or document text for Q&A analysis",
    )
    enable_web_research: bool = Field(
        default=True,
        description="Combine internal documents with public web research",
    )


class AgentStep(BaseModel):
    step_number: int
    action: str
    tool_name: str
    arguments: Dict[str, Any]
    output: Any


class AgentRunResponse(BaseModel):
    task: str
    status: str
    steps: List[AgentStep]
    final_synthesis: str
    execution_time_ms: float


@router.post(
    "/run",
    response_model=AgentRunResponse,
    summary="Execute autonomous AI Data Analyst & Web Researcher workflow (RBAC Protected)"
)
async def run_autonomous_agent(
    request: AgentRunRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> AgentRunResponse:
    # 1. Enforce RBAC Permission Guard
    PermissionChecker(Permission.TOOLS_EXECUTE)(current_user.role)
    PermissionChecker(Permission.CHAT_INFER)(current_user.role)

    start_time = time.time()
    task = request.task_description
    task_lower = task.lower()
    doc_content = request.document_payload

    steps: List[AgentStep] = []

    # 1. AI Document + Web Researcher Workflow (Triggered when document is attached or research keywords present)
    has_research_keyword = any(k in task_lower for k in ["search", "research", "web", "csv", "pdf", "document"])
    if doc_content or has_research_keyword:
        payload_to_use = doc_content if doc_content else ""
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="pdf_csv_web_researcher",
                arguments={
                    "document_content": payload_to_use,
                    "question": task,
                    "enable_web_search": request.enable_web_research,
                }
            )
        )
        steps.append(
            AgentStep(
                step_number=1,
                action="AI Document & Web Research",
                tool_name="pdf_csv_web_researcher",
                arguments={"document_content": payload_to_use[:100] + "..." if payload_to_use else "None", "question": task, "web_search": request.enable_web_research},
                output=exec_res.result,
            )
        )

    # 2. AI Data Analyst & SQL Agent Workflow
    if "sql" in task_lower or "query" in task_lower or "postgres" in task_lower or "snowflake" in task_lower or "bigquery" in task_lower or "calculate" in task_lower or "metric" in task_lower:
        sql_task_type = "generate_sql"
        if "translate" in task_lower or "convert" in task_lower:
            sql_task_type = "translate_sql"
        elif "explain" in task_lower or "plan" in task_lower or "optimize" in task_lower:
            sql_task_type = "explain_plan"
        elif "calculate" in task_lower or "metric" in task_lower:
            sql_task_type = "calculate_metric"

        dialect = "snowflake" if "snowflake" in task_lower else ("bigquery" if "bigquery" in task_lower else "postgres")

        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="sql_data_analyst_tool",
                arguments={"task": sql_task_type, "query_or_prompt": task, "dialect": dialect}
            )
        )
        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                action=f"AI Data Analyst ({sql_task_type.title()})",
                tool_name="sql_data_analyst_tool",
                arguments={"task": sql_task_type, "query_or_prompt": task, "dialect": dialect},
                output=exec_res.result,
            )
        )

    # 3. Data Schema Validator Workflow
    if "json" in task_lower or "validate" in task_lower or "schema" in task_lower:
        sample_json = '{"record_id": "rec-101", "user_email": "user@data.io", "amount": 250.50, "status": "ACTIVE"}'
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="data_schema_validator",
                arguments={"json_payload": sample_json}
            )
        )
        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                action="Schema Quality Validation",
                tool_name="data_schema_validator",
                arguments={"json_payload": sample_json},
                output=exec_res.result,
            )
        )

    # 4. Text Summarization Workflow
    if "summary" in task_lower or "summarize" in task_lower:
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="text_summarizer",
                arguments={"text": task, "style": "executive"}
            )
        )
        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                action="Text Summarization",
                tool_name="text_summarizer",
                arguments={"text": task, "style": "executive"},
                output=exec_res.result,
            )
        )

    # Grounded answer computed from the uploaded document (if the document tool ran)
    grounded_answer = next(
        (
            s.output.get("grounded_answer")
            for s in steps
            if s.tool_name == "pdf_csv_web_researcher" and isinstance(s.output, dict)
        ),
        None,
    )

    # Synthesize Final LLM Completion based on Autonomous Telemetry & Web Sources
    findings_str = "\n".join([f"Step {s.step_number} [{s.action}]: Tool '{s.tool_name}' output: {s.output}" for s in steps])

    prompt_messages = [
        ChatMessage(
            role="system",
            content=(
                "You are an Enterprise AI Data Analyst & Web Researcher Agent. Answer ONLY from the "
                "tool findings below. If a fact is not in the findings, say it was not found."
            ),
        ),
        ChatMessage(
            role="user",
            content=f"Task Goal: {task}\nCollected Telemetry & Web Knowledge:\n{findings_str or 'No specific tool triggers fired.'}\nProvide final synthesis.",
        ),
    ]

    llm_resp = await llm_service.generate_completion(
        ChatCompletionRequest(model=request.model, messages=prompt_messages)
    )
    final_text = llm_resp.choices[0].message.content

    # Without a real model backend, return the answer computed directly from the file
    # rather than templated text.
    if grounded_answer and llm_resp.backend == "local_fast_engine":
        final_text = grounded_answer

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return AgentRunResponse(
        task=task,
        status="COMPLETED",
        steps=steps,
        final_synthesis=final_text,
        execution_time_ms=elapsed_ms,
    )
