import time
from typing import Annotated, Any, Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.api.v1.auth import get_current_user
from app.core.rbac import Permission, PermissionChecker
from app.models.auth import UserInDB
from app.models.chat import ChatCompletionRequest, ChatMessage
from app.models.tools import ToolExecutionRequest
from app.services.audit_service import audit_logger
from app.services.llm_service import llm_service
from app.services.tool_service import tool_service

router = APIRouter(prefix="/agent", tags=["Autonomous AI Agent"])


class AgentRunRequest(BaseModel):
    task_description: str = Field(
        ...,
        description="Goal or investigation prompt for the autonomous agent",
        json_schema_extra={"example": "Scan IP address 45.33.32.156 for threat intelligence and assess risk."},
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
    summary="Execute autonomous multi-tool AI security workflow (RBAC Protected)"
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

    # Autonomous Tool Selection Routing
    if "ip" in task_lower or "address" in task_lower or "scan" in task_lower:
        import re
        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", task)
        target_ip = ip_match.group(0) if ip_match else "45.33.32.156"

        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(tool_name="ip_threat_lookup", arguments={"ip_address": target_ip})
        )
        steps.append(
            AgentStep(
                step_number=1,
                action="Tool Execution",
                tool_name="ip_threat_lookup",
                arguments={"ip_address": target_ip},
                output=exec_res.result,
            )
        )

    if "code" in task_lower or "eval" in task_lower or "vulnerability" in task_lower or "secret" in task_lower:
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(tool_name="vulnerability_scanner", arguments={"code_snippet": task})
        )
        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                action="Tool Execution",
                tool_name="vulnerability_scanner",
                arguments={"code_snippet": task},
                output=exec_res.result,
            )
        )

    if "compliance" in task_lower or "soc2" in task_lower or "hipaa" in task_lower:
        exec_res = tool_service.execute_tool(
            ToolExecutionRequest(tool_name="compliance_evaluator", arguments={"policy_text": task})
        )
        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                action="Tool Execution",
                tool_name="compliance_evaluator",
                arguments={"policy_text": task},
                output=exec_res.result,
            )
        )

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
            content="You are an Enterprise Autonomous AI Agent. Synthesize tool telemetry into a clean executive summary.",
        ),
        ChatMessage(
            role="user",
            content=f"Task Goal: {task}\nCollected Autonomous Evidence:\n{findings_str or 'No specific tool triggers fired.'}\nProvide final synthesis.",
        ),
    ]

    llm_resp = await llm_service.generate_completion(
        ChatCompletionRequest(model=request.model, messages=prompt_messages)
    )

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    audit_logger.log(
        user_id=current_user.username,
        action="AUTONOMOUS_AGENT_EXECUTION",
        resource="/agent/run",
        status="SUCCESS",
        details={"task": task, "steps_executed": len(steps), "latency_ms": elapsed_ms},
    )

    return AgentRunResponse(
        task=task,
        status="COMPLETED",
        steps=steps,
        final_synthesis=llm_resp.choices[0].message.content,
        execution_time_ms=elapsed_ms,
    )
