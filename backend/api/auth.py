import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db.base import get_db
from backend.models.models import User
from backend.schemas.auth import LoginRequest, TokenData, StandardResponse
from backend.core.exceptions import raise_http_exception
from backend.core.dependencies import verify_password, create_access_token

logger = structlog.get_logger("raptor_ledger.api.auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=StandardResponse[TokenData])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Verifies incoming user profiles and issues JWT authorization context layers."""
    logger.info("Processing ingestion authentication request context", email=payload.email)

    query = select(User).where(User.email == payload.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        logger.warn("Identity verification rejected: invalid credentials match", email=payload.email)
        raise_http_exception(
            status_code=401,
            error_code="INVALID_CREDENTIALS",
            message="Invalid username credentials or secure matching pass phrase pairing context."
        )

    # Token issuance matrices boundary allocations
    token_payload = {"sub": user.email, "user_id": str(user.id)}
    access_token = create_access_token(data=token_payload)

    logger.info("User identity validated successfully. Access token granted.", user_id=str(user.id))
    return StandardResponse(
        success=True,
        message="Authentication token context minted successfully.",
        data=TokenData(access_token=access_token)
    )


@router.post("/logout", response_model=StandardResponse[None])
async def logout():
    """Stateless logout implementation boundary interface context tracking."""
    return StandardResponse(
        success=True,
        message="Session terminated successfully on server boundaries. Client layer clear required.",
        data=None
    )
