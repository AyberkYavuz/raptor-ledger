import pytest
import pytest_asyncio
from uuid import uuid4
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.db.base import Base
from backend.models.models import User
from backend.core.config import settings
from backend.core.dependencies import hash_password, verify_password, create_access_token, get_current_user
from backend.core.exceptions import HTTPExceptionWithCode

# Local micro test isolation tracking matrix engine
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.unit
def test_cryptographic_password_hashing_boundary():
    """Confirms irreversible passphrases salt and resolve match criteria correctly."""
    secret = "mamba_mentality_2026"
    hashed = hash_password(secret)

    assert hashed != secret
    assert verify_password(secret, hashed) is True
    assert verify_password("wrong_phrase", hashed) is False


@pytest.mark.unit
def test_jwt_token_minting_and_claim_extraction():
    """Validates serialized token claims decode precisely across operational matrices."""
    claims = {"sub": "ayberk@raptor.ai", "scope": "operator"}
    token = create_access_token(data=claims)

    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert decoded["sub"] == "ayberk@raptor.ai"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_get_current_user_unauthorized_boundary_conditions():
    """Ensures empty parameters throw structured boundary evaluation tracking exceptions."""
    # Instantiating dummy database connection session context vectors
    mock_session = None

    with pytest.raises(HTTPExceptionWithCode) as exc_info:
        await get_current_user(token=None, db=mock_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"
