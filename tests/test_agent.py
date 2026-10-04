from typing import Dict
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_run_autonomous_agent(async_client: AsyncClient, auth_headers: Dict[str, str]) -> None:
    response = await async_client.post(
        "/api/v1/agent/run",
        headers=auth_headers,
        json={
            "task_description": "Generate top revenue customer SQL query in Postgres and validate JSON schema.",
            "model": "llama3-open-8b",
            "enable_web_research": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert len(data["steps"]) >= 1
    assert "final_synthesis" in data
