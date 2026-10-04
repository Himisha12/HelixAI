from typing import Dict
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_run_autonomous_agent(async_client: AsyncClient, auth_headers: Dict[str, str]) -> None:
    response = await async_client.post(
        "/api/v1/agent/run",
        headers=auth_headers,
        json={
            "task_description": "Scan IP address 45.33.32.156 for threat intelligence and evaluate risk.",
            "model": "llama3-open-8b",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert len(data["steps"]) >= 1
    assert data["steps"][0]["tool_name"] == "ip_threat_lookup"
    assert "final_synthesis" in data
