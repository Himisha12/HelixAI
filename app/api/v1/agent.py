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

router = APIRouter(prefix="/agent", tags=["Autonomous Data AI Agent"])


class AgentRunRequest(BaseModel):
    task_description: str = Field(
        ...,
        description="Goal prompt for the autonomous data engineering agent",
        json_schema_extra={"example": "Generate top customer revenue query in Postgres and validate sample JSON records."},
    )
    model: str = Field(default="llama3-open-8b")


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
    summary="Execute autonomous data engineering AI workflow (RBAC Protected)"
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

    steps: List[AgentStep] = []

    # Autonomous Tool Selection Routing for Data Engineering Workflows
    if "sql" in task_lower or "query" in task_lower or "revenue" in task_lower or "postgres" in task_lower or "snowflake" in task_lower:
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="sql_query_generator",
                arguments={"data_request": task, "dialect": "postgres"}
            )
        )
        steps.append(
            AgentStep(
                step_number=1,
                action="Tool Execution",
                tool_name="sql_query_generator",
                arguments={"data_request": task, "dialect": "postgres"},
                output=exec_res.result,
            )
        )

    if "json" in task_lower or "schema" in task_lower or "validate" in task_lower or "record" in task_lower:
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
                action="Tool Execution",
                tool_name="data_schema_validator",
                arguments={"json_payload": sample_json},
                output=exec_res.result,
            )
        )

    if "csv" in task_lower or "tabular" in task_lower or "profile" in task_lower:
        sample_csv = "id,name,revenue\n1,Alpha Corp,5000\n2,Beta Inc,12000"
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="csv_data_analyzer",
                arguments={"csv_text": sample_csv}
            )
        )
        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                action="Tool Execution",
                tool_name="csv_data_analyzer",
                arguments={"csv_text": sample_csv},
                output=exec_res.result,
            )
        )

    if "summary" in task_lower or "summarize" in task_lower or "text" in task_lower:
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(
                tool_name="text_summarizer",
                arguments={"text": task, "style": "executive"}
            )
        )
        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                action="Tool Execution",
                tool_name="text_summarizer",
                arguments={"text": task, "style": "executive"},
                output=exec_res.result,
            )
        )

    if not steps:
        # Fallback to calculator if numbers present
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
                    action="Tool Execution",
                    tool_name="calculator",
                    arguments={"expression": expr},
                    output=exec_res.result,
                )
            )

    # Synthesize Final Model Completion based on Autonomous Tool Findings
    findings_str = "\n".join([f"Step {s.step_number}: Tool '{s.tool_name}' returned: {s.output}" for s in steps])

    prompt_messages = [
        ChatMessage(
            role="system",
            content="You are an Enterprise Autonomous Data AI Agent. Synthesize tool execution telemetry into a clear executive summary.",
        ),
        ChatMessage(
            role="user",
            content=f"Task Goal: {task}\nCollected Autonomous Telemetry:\n{findings_str or 'No specific tool triggers fired.'}\nProvide final synthesis.",
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
