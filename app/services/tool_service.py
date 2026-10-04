import ast
import operator
import re
import sys
import time
from typing import Any, Callable, Dict, List, Optional
from app.models.tools import (
    ToolDefinition,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ToolParameter,
)

# Binary operators mapping
BINARY_OPERATORS: Dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

# Unary operators mapping
UNARY_OPERATORS: Dict[type, Callable[[Any], Any]] = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        bin_op_type = type(node.op)
        if bin_op_type in BINARY_OPERATORS:
            return BINARY_OPERATORS[bin_op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {bin_op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval(node.operand)
        unary_op_type = type(node.op)
        if unary_op_type in UNARY_OPERATORS:
            return UNARY_OPERATORS[unary_op_type](operand)
        raise ValueError(f"Unsupported unary operator: {unary_op_type}")
    else:
        raise ValueError(f"Unsupported expression element: {type(node)}")


class ToolService:
    """
    Independent Tool Execution Service boundary with predefined tool registry,
    parameter validation, and safe sandboxed execution handlers.
    Includes Enterprise Security, Compliance, Threat Intelligence, and System Tools.
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
        self._tools["ip_threat_lookup"] = ToolDefinition(
            name="ip_threat_lookup",
            description="Lookup threat intelligence risk score and abuse telemetry for an IP address",
            parameters={
                "ip_address": ToolParameter(
                    type="string", description="IP address to scan (e.g. '192.168.1.1' or '45.33.32.156')"
                )
            },
        )
        self._tools["vulnerability_scanner"] = ToolDefinition(
            name="vulnerability_scanner",
            description="Perform static security analysis on code snippet for hardcoded secrets and OWASP vulnerabilities",
            parameters={
                "code_snippet": ToolParameter(
                    type="string", description="Source code text to scan for security risks"
                )
            },
        )
        self._tools["compliance_evaluator"] = ToolDefinition(
            name="compliance_evaluator",
            description="Evaluate policy description against SOC2, HIPAA, and GDPR regulatory controls",
            parameters={
                "policy_text": ToolParameter(
                    type="string", description="Security or data retention policy text"
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

            elif tool_name == "ip_threat_lookup":
                ip = str(args.get("ip_address", "0.0.0.0")).strip()
                # Mock threat DB lookup
                is_malicious = ip.startswith("45.") or ip.startswith("185.") or "bad" in ip
                risk_score = 88 if is_malicious else 12
                threat_tags = ["Botnet Host", "SSH Brute-force"] if is_malicious else ["Clean IP", "Residential ISP"]
                
                return ToolExecutionResponse(
                    tool_name=tool_name,
                    status="success",
                    result={
                        "ip_address": ip,
                        "risk_score": risk_score,
                        "risk_level": "HIGH" if is_malicious else "LOW",
                        "threat_tags": threat_tags,
                        "country": "Germany" if is_malicious else "United States",
                        "last_scanned": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    },
                )

            elif tool_name == "vulnerability_scanner":
                code = str(args.get("code_snippet", ""))
                vulnerabilities: List[Dict[str, str]] = []

                if "eval(" in code or "exec(" in code:
                    vulnerabilities.append({
                        "issue": "Arbitrary Code Execution Risk",
                        "severity": "CRITICAL",
                        "recommendation": "Avoid using eval() or exec(). Use AST safe evaluation instead."
                    })
                if re.search(r"secret|password|api_key|token\s*=\s*['\"][^'\"]+['\"]", code, re.IGNORECASE):
                    vulnerabilities.append({
                        "issue": "Hardcoded Credential Exposure",
                        "severity": "HIGH",
                        "recommendation": "Store sensitive secrets in environment variables using Pydantic Settings."
                    })
                if "SELECT" in code and "%s" not in code and "?" not in code and "+" in code:
                    vulnerabilities.append({
                        "issue": "Potential SQL Injection Vulnerability",
                        "severity": "HIGH",
                        "recommendation": "Use parameterized queries or an ORM like SQLAlchemy."
                    })

                if not vulnerabilities:
                    vulnerabilities.append({
                        "issue": "No Obvious Vulnerabilities Detected",
                        "severity": "INFO",
                        "recommendation": "Code passes basic static security checks."
                    })

                return ToolExecutionResponse(
                    tool_name=tool_name,
                    status="success",
                    result={
                        "scan_status": "COMPLETED",
                        "findings_count": len(vulnerabilities),
                        "vulnerabilities": vulnerabilities,
                    },
                )

            elif tool_name == "compliance_evaluator":
                text = str(args.get("policy_text", ""))
                has_encryption = "encrypt" in text.lower() or "tls" in text.lower() or "aes" in text.lower()
                has_audit = "log" in text.lower() or "audit" in text.lower()
                has_rbac = "role" in text.lower() or "access" in text.lower() or "rbac" in text.lower()

                controls = [
                    {"control": "SOC2 CC6.1 - Access Controls & RBAC", "status": "PASS" if has_rbac else "FAIL"},
                    {"control": "SOC2 CC6.6 - Data Encryption in Transit & Rest", "status": "PASS" if has_encryption else "FAIL"},
                    {"control": "HIPAA 164.312(b) - Audit Controls", "status": "PASS" if has_audit else "FAIL"},
                ]

                return ToolExecutionResponse(
                    tool_name=tool_name,
                    status="success",
                    result={
                        "evaluation": "SOC2 & HIPAA Compliance Audit",
                        "overall_score": f"{sum(1 for c in controls if c['status'] == 'PASS')}/3 Controls Met",
                        "controls": controls,
                    },
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
