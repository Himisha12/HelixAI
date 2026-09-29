import ast
import operator
import sys
import time
from typing import Any, Dict, List, Optional
from app.models.tools import (
    ToolDefinition,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ToolParameter,
)

# Safe math operators for AST evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Num):  # Python < 3.8 back-compat
        return node.n
    elif isinstance(node, ast.Constant):  # Python >= 3.8
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported operator: {op_type}")
    else:
        raise ValueError(f"Unsupported expression element: {type(node)}")


class ToolService:
    """
    Independent Tool Execution Service boundary with predefined tool registry,
    parameter validation, and safe sandboxed execution handlers.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        self._tools["calculator"] = ToolDefinition(
            name="calculator",
            description="Perform safe numerical and mathematical evaluations (e.g. '25 * 4 + 10')",
            parameters={
                "expression": ToolParameter(
                    type="string", description="Mathematical expression to evaluate"
                )
            },
        )
        self._tools["weather_lookup"] = ToolDefinition(
            name="weather_lookup",
            description="Lookup real-time mock weather data for a specified city",
            parameters={
                "city": ToolParameter(
                    type="string", description="Target city name (e.g. San Francisco, Tokyo, London)"
                )
            },
        )
        self._tools["system_info"] = ToolDefinition(
            name="system_info",
            description="Retrieve active microservice engine runtime environment metrics",
            parameters={},
        )
        self._tools["text_summarizer"] = ToolDefinition(
            name="text_summarizer",
            description="Extract concise key summary bullet points from text input",
            parameters={
                "text": ToolParameter(
                    type="string", description="Text payload to summarize"
                )
            },
        )

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResponse:
        tool_name = request.tool_name
        args = request.arguments

        if tool_name not in self._tools:
            return ToolExecutionResponse(
                tool_name=tool_name,
                status="error",
                result=None,
                error=f"Tool '{tool_name}' is not registered in the system registry.",
            )

        try:
            if tool_name == "calculator":
                expr = str(args.get("expression", ""))
                parsed = ast.parse(expr, mode="eval")
                val = _safe_eval(parsed.body)
                return ToolExecutionResponse(
                    tool_name=tool_name, status="success", result={"expression": expr, "value": val}
                )

            elif tool_name == "weather_lookup":
                city = str(args.get("city", "Unknown City")).title()
                # Mock weather database generator
                mock_weather = {
                    "city": city,
                    "temperature": "22°C / 71.6°F",
                    "condition": "Partly Cloudy",
                    "humidity": "58%",
                    "wind_speed": "12 km/h",
                }
                return ToolExecutionResponse(
                    tool_name=tool_name, status="success", result=mock_weather
                )

            elif tool_name == "system_info":
                info = {
                    "python_version": sys.version.split()[0],
                    "server_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "status": "healthy",
                    "supported_backends": ["local_mock", "ollama", "huggingface", "openrouter"],
                }
                return ToolExecutionResponse(
                    tool_name=tool_name, status="success", result=info
                )

            elif tool_name == "text_summarizer":
                text = str(args.get("text", ""))
                sentences = [s.strip() for s in text.split(".") if s.strip()]
                summary = sentences[:3] if len(sentences) >= 3 else sentences
                return ToolExecutionResponse(
                    tool_name=tool_name,
                    status="success",
                    result={"summary_bullets": summary, "original_length": len(text)},
                )

            else:
                return ToolExecutionResponse(
                    tool_name=tool_name,
                    status="error",
                    result=None,
                    error=f"No execution handler implemented for tool '{tool_name}'.",
                )

        except Exception as e:
            return ToolExecutionResponse(
                tool_name=tool_name,
                status="error",
                result=None,
                error=f"Tool execution failed: {str(e)}",
            )


# Global tool service instance
tool_service = ToolService()
