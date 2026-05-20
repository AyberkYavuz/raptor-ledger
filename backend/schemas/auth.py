# backend/schemas/auth.py
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, EmailStr, Field

T = TypeVar('T')


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StandardResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error_code: Optional[str] = None
