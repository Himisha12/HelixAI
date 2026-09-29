from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    type: str
    description: str
    required: bool = True


class ToolDefinition(BaseModel):
    name: str = Field(..., description="Unique tool identifier name")
    description: str = Field(..., description="Human-readable explanation of tool behavior")
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict)


class ToolCall(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments dictionary")


class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResponse(BaseModel):
    tool_name: str
    status: str = "success"
    result: Any
    error: Optional[str] = None
