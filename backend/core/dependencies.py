import structlog
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.core.config import settings
from backend.core.exceptions import raise_http_exception
from backend.db.base import get_db
from backend.models.models import User

logger = structlog.get_logger("raptor_ledger.core.dependencies")

# Instantiate secure hashing strategies
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Expose security headers endpoint injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """Computes an irreversible secure salt-hash of plaintext passwords."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validates an incoming plaintext string against a verified hash profile."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates an authenticated JWT verification matrix signature payload."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Security dependency ensuring incoming token signatures authenticate smoothly."""
    if not token:
        logger.warn("Missing security header token parameter boundary.")
        raise_http_exception(
            status_code=401,
            error_code="UNAUTHORIZED",
            message="Authentication credentials token parameter missing or unset."
        )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warn("Token payload claim validation missing identity string context.")
            raise_http_exception(
                status_code=401,
                error_code="UNAUTHORIZED",
                message="Invalid verification claims signature contextual matrix."
            )
    except JWTError as e:
        logger.warn("Cryptographic verification trace invalid or expired.", error=str(e))
        raise_http_exception(
            status_code=401,
            error_code="UNAUTHORIZED",
            message="Token signature has completely expired or holds corrupt structures."
        )

    # Context query parsing inside relational async boundaries
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        logger.error("Authenticated identity claim target record cannot be resolved.", user_email=email)
        raise_http_exception(
            status_code=401,
            error_code="UNAUTHORIZED",
            message="System user resource record no longer exists inside this node instance."
        )

    return user
