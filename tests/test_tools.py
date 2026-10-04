from typing import Dict
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tools(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    tool_names = [t["name"] for t in data]
    assert "pdf_csv_analyzer" in tool_names
    assert "sql_agent_tool" in tool_names
    assert "data_schema_validator" in tool_names
    assert "text_summarizer" in tool_names
    assert "calculator" in tool_names


@pytest.mark.asyncio
async def test_execute_pdf_csv_analyzer_tool(
    async_client: AsyncClient, auth_headers: Dict[str, str]
) -> None:
    response = await async_client.post(
        "/api/v1/tools/execute",
        headers=auth_headers,
        json={
            "tool_name": "pdf_csv_analyzer",
            "arguments": {
                "document_content": "id,customer,revenue\n101,Acme,125000\n102,Globex,85000",
                "question": "What is the total revenue?",
                "file_type": "csv"
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["file_type"] == "csv"


@pytest.mark.asyncio
async def test_execute_sql_agent_tool(
    async_client: AsyncClient, auth_headers: Dict[str, str]
) -> None:
    response = await async_client.post(
        "/api/v1/tools/execute",
        headers=auth_headers,
        json={
            "tool_name": "sql_agent_tool",
            "arguments": {
                "task": "generate",
                "prompt_or_query": "Top 5 revenue customers in Postgres",
                "dialect": "postgres"
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "SELECT" in data["result"]["generated_sql"]


@pytest.mark.asyncio
async def test_execute_data_schema_validator_tool(
    async_client: AsyncClient, auth_headers: Dict[str, str]
) -> None:
    response = await async_client.post(
        "/api/v1/tools/execute",
        headers=auth_headers,
        json={
            "tool_name": "data_schema_validator",
            "arguments": {"json_payload": '{"id": 101, "email": "test@data.io", "amount": 99.5}'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["is_valid_json"] is True


@pytest.mark.asyncio
async def test_execute_calculator_tool(
    async_client: AsyncClient, auth_headers: Dict[str, str]
) -> None:
    response = await async_client.post(
        "/api/v1/tools/execute",
        headers=auth_headers,
        json={"tool_name": "calculator", "arguments": {"expression": "10 * 5 + 25"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["value"] == 75
