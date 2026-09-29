import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tools(async_client: AsyncClient):
    response = await async_client.get("/api/v1/tools")
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) >= 3
    tool_names = [t["name"] for t in tools]
    assert "calculator" in tool_names
    assert "weather_lookup" in tool_names
    assert "system_info" in tool_names


@pytest.mark.asyncio
async def test_execute_calculator_tool(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.post(
        "/api/v1/tools/execute",
        headers=auth_headers,
        json={"tool_name": "calculator", "arguments": {"expression": "10 * 5 + 25"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["value"] == 75


@pytest.mark.asyncio
async def test_execute_weather_tool(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.post(
        "/api/v1/tools/execute",
        headers=auth_headers,
        json={"tool_name": "weather_lookup", "arguments": {"city": "Tokyo"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["city"] == "Tokyo"
