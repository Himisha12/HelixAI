from typing import Dict
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_completion_unauthorized(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/chat/completions",
        json={
            "model": "llama3-open-8b",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_completion_authorized(async_client: AsyncClient, auth_headers: Dict[str, str]) -> None:
    response = await async_client.post(
        "/api/v1/chat/completions",
        headers=auth_headers,
        json={
            "model": "llama3-open-8b",
            "messages": [{"role": "user", "content": "What is the capital of France?"}],
            "temperature": 0.5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "llama3-open-8b"
    assert len(data["choices"]) > 0
    assert "usage" in data
    assert data["usage"]["total_tokens"] > 0


@pytest.mark.asyncio
async def test_chat_completion_structured_json(async_client: AsyncClient, auth_headers: Dict[str, str]) -> None:
    response = await async_client.post(
        "/api/v1/chat/completions",
        headers=auth_headers,
        json={
            "model": "mistral-7b-open",
            "messages": [{"role": "user", "content": "Provide json summary"}],
            "structured_json": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    assert "status" in content
