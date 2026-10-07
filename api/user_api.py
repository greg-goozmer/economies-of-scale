import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from schemas.user import UserCredentials, UserRead, UserRegister


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    user_name = payload.user_name.strip()
    if not user_name:
        raise HTTPException(422, "User name is required")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", payload.password.encode(),
                                 bytes.fromhex(salt), 300_000).hex()
    user = User(user_name=user_name,
                user_password_hash=f"pbkdf2_sha256${salt}${digest}")
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(409, "User name already exists") from error
    return UserRead(user_id=user.user_id, user_name=user.user_name)


@router.post("/auth", status_code=status.HTTP_204_NO_CONTENT)
async def authenticate_user(_payload: UserCredentials):
    """LR4 placeholder: authentication is not active in LR3."""


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user():
    """LR4 placeholder: there is no session to clear in LR3."""
