from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from typing import Optional
from ..db import get_session
from ..models import User
from .jwt import verify_token


def get_current_user(
    session: Session = Depends(get_session),
    access_token: Optional[str] = Cookie(None, alias="access_token")
) -> User:
    """Get current authenticated user from token"""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(access_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def get_current_user_optional(
    session: Session = Depends(get_session),
    access_token: Optional[str] = Cookie(None, alias="access_token")
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    try:
        return get_current_user(session, access_token)
    except HTTPException:
        return None