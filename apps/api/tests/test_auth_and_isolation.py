import pytest
from httpx import AsyncClient, ASGITransport
from verifyd.main import app
from verifyd.core.security import hash_password, verify_password, create_access_token, decode_token
from verifyd.core.errors import NotFoundError, PermissionDeniedError

def test_password_hashing():
    pwd = "Verifyd!2026"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPass123", hashed) is False

def test_jwt_token_lifecycle():
    user_payload = {
        "sub": "user-123",
        "email": "sarah@lumenskincare.com",
        "role": "company_member",
        "org_id": "org-lumen",
    }
    token = create_access_token(user_payload)
    decoded = decode_token(token)
    assert decoded["sub"] == "user-123"
    assert decoded["email"] == "sarah@lumenskincare.com"
    assert decoded["role"] == "company_member"
    assert decoded["org_id"] == "org-lumen"

@pytest.mark.asyncio
async def test_auth_login_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Successful login
        res = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@lumenskincare.com", "password": "Verifyd!2026"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "admin@lumenskincare.com"

        # 2. Failed login returns standard error envelope with 401
        failed_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@lumenskincare.com", "password": "BadPassword!"},
        )
        assert failed_res.status_code == 401
        err_data = failed_res.json()
        assert "error" in err_data
        assert err_data["error"]["code"] == "UNAUTHORIZED"
