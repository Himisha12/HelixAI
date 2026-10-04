from typing import Dict
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_audit_logs_as_auditor(async_client: AsyncClient) -> None:
    # Login as auditor_user (Role: auditor)
    login_resp = await async_client.post(
        "/api/v1/auth/token",
        data={"username": "auditor_user", "password": "audit123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    auditor_headers = {"Authorization": f"Bearer {token}"}

    audit_resp = await async_client.get("/api/v1/audit-logs", headers=auditor_headers)
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert isinstance(logs, list)
    assert len(logs) > 0


@pytest.mark.asyncio
async def test_get_audit_logs_denied_for_regular_user(async_client: AsyncClient, auth_headers: Dict[str, str]) -> None:
    # demo_user has role 'user', which lacks audit:read permission
    audit_resp = await async_client.get("/api/v1/audit-logs", headers=auth_headers)
    assert audit_resp.status_code == 403
    assert "Permission denied" in audit_resp.json()["detail"]
