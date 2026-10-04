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

router = APIRouter(prefix="/agent", tags=["Autonomous SQL & Data AI Agent"])


class AgentRunRequest(BaseModel):
    task_description: str = Field(
        ...,
        description="Goal prompt for the autonomous SQL & Data AI Agent",
        json_schema_extra={"example": "Generate top regional customer revenue query in Snowflake and translate to Postgres."},
    )
    model: str = Field(default="llama3-open-8b")
    document_payload: str = Field(
        default="",
        description="Optional uploaded CSV or document text for Q&A analysis",
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
    summary="Execute autonomous SQL & Data AI Agent workflow (RBAC Protected)"
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

    # 1. Document / CSV Reader & Q&A Workflow
    if doc_content or "csv" in task_lower or "pdf" in task_lower or "document" in task_lower or "file" in task_lower or "read" in task_lower:
        payload_to_use = doc_content if doc_content else "id,customer_name,revenue,region\n101,Acme Corp,125000,US-East\n102,Globex,85000,US-West\n103,Soylent,210000,EU-Central"
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="pdf_csv_analyzer",
                arguments={
                    "document_content": payload_to_use,
                    "question": task,
                    "file_type": "csv" if "," in payload_to_use.split("\n")[0] else "pdf"
                }
            )
        )
        steps.append(
            AgentStep(
                step_number=1,
                action="Document & CSV Analysis",
                tool_name="pdf_csv_analyzer",
                arguments={"document_content": payload_to_use[:100] + "...", "question": task},
                output=exec_res.result,
            )
        )

    # 2. SQL AI Agent Query Generation, Translation & Plan Analysis
    if "sql" in task_lower or "query" in task_lower or "postgres" in task_lower or "snowflake" in task_lower or "bigquery" in task_lower or "table" in task_lower:
        sql_task_type = "generate"
        if "translate" in task_lower or "convert" in task_lower:
            sql_task_type = "translate"
        elif "explain" in task_lower or "plan" in task_lower or "optimize" in task_lower:
            sql_task_type = "explain_plan"
        elif "ddl" in task_lower or "schema" in task_lower or "create" in task_lower:
            sql_task_type = "generate_ddl"

        dialect = "snowflake" if "snowflake" in task_lower else ("bigquery" if "bigquery" in task_lower else "postgres")

        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="sql_agent_tool",
                arguments={"task": sql_task_type, "prompt_or_query": task, "dialect": dialect}
            )
        )
        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                action=f"SQL Agent ({sql_task_type.title()})",
                tool_name="sql_agent_tool",
                arguments={"task": sql_task_type, "prompt_or_query": task, "dialect": dialect},
                output=exec_res.result,
            )
        )

    # 3. JSON Schema Validation Workflow
    if "json" in task_lower or "validate" in task_lower or "record" in task_lower:
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

    # 5. Math Calculation Fallback
    if not steps:
        import re
        if any(op in task for op in ["+", "*", "-", "/"]) and any(c.isdigit() for c in task):
            math_match = re.search(r"[\d\s\+\-\*\/\(\)]+", task)
            expr = math_match.group(0).strip() if math_match else "10 * 5"
            exec_res = tool_service.execute_tool(
                ToolExecutionRequest(tool_name="calculator", arguments={"expression": expr})
            )
            steps.append(
                AgentStep(
                    step_number=1,
                    action="Math Formula Execution",
                    tool_name="calculator",
                    arguments={"expression": expr},
                    output=exec_res.result,
                )
            )

    # Synthesize Final LLM Completion based on Autonomous Agent Telemetry
    findings_str = "\n".join([f"Step {s.step_number} [{s.action}]: Tool '{s.tool_name}' output: {s.output}" for s in steps])

    prompt_messages = [
        ChatMessage(
            role="system",
            content="You are an Enterprise Autonomous SQL & Data AI Agent. Synthesize tool telemetry into a clean executive report.",
        ),
        ChatMessage(
            role="user",
            content=f"Task Goal: {task}\nCollected Autonomous Telemetry:\n{findings_str or 'No specific tool triggers fired.'}\nProvide final executive summary and technical recommendations.",
        ),
    ]

    llm_resp = await llm_service.generate_completion(
        ChatCompletionRequest(model=request.model, messages=prompt_messages)
    )

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return AgentRunResponse(
        task=task,
        status="COMPLETED",
        steps=steps,
        final_synthesis=llm_resp.choices[0].message.content,
        execution_time_ms=elapsed_ms,
    )
