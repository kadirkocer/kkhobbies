from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from ..auth import hash_password, verify_password, create_access_token
from ..db import get_session
from ..models import User
from ..schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(
    credentials: LoginRequest,
    response: Response,
    session: Session = Depends(get_session)
):
    """Login and get access token"""
    # For single user app, get the first (and only) user
    user = session.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No user found. Initialize the application first."
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        samesite="lax"
    )
    
    return {"message": "Login successful"}


@router.post("/logout")
def logout(response: Response):
    """Logout by clearing the access token cookie"""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}