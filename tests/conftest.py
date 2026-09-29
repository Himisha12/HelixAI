from typing import AsyncGenerator, Dict
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    token = create_access_token(data={"sub": "demo_user", "role": "user"})
    return {"Authorization": f"Bearer {token}"}
