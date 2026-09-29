import time
import uuid
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"] = Field(
        ..., description="Role of the message author"
    )
    content: str = Field(..., description="Text content of the message")
    name: Optional[str] = Field(default=None, description="Optional author name or tool name")


class ChatCompletionRequest(BaseModel):
    model: str = Field(
        default="llama3-open-8b",
        description="ID of the model to use (e.g. llama3-open-8b, mistral-7b-open, phi3-mini-open)"
    )
    messages: List[ChatMessage] = Field(
        ..., min_length=1, description="List of messages comprising the conversation history"
    )
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature between 0 and 2"
    )
    max_tokens: int = Field(
        default=512, ge=1, le=4096, description="Maximum number of tokens to generate"
    )
    stream: bool = Field(
        default=False, description="Whether to stream back partial progress"
    )
    system_prompt_template: Optional[str] = Field(
        default=None, description="Optional custom system instruction template override"
    )
    structured_json: bool = Field(
        default=False, description="Enforce structured JSON schema output"
    )

    @field_validator("messages")
    @classmethod
    def validate_messages_not_empty(cls, v: List[ChatMessage]) -> List[ChatMessage]:
        if not v:
            raise ValueError("Messages list cannot be empty.")
        return v


class UsageInfo(BaseModel):
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the generated completion")
    total_tokens: int = Field(..., description="Total tokens used in request")
    latency_ms: float = Field(..., description="Execution latency in milliseconds")


class ChoiceMessage(BaseModel):
    role: str = "assistant"
    content: str


class Choice(BaseModel):
    index: int = 0
    message: ChoiceMessage
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:12]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    backend: str = Field(..., description="Backend engine executed (local_mock, ollama, etc.)")
    choices: List[Choice]
    usage: UsageInfo


class ModelInfo(BaseModel):
    id: str
    name: str
    backend: str
    context_window: int = 8192
    description: str
    is_local: bool = True
