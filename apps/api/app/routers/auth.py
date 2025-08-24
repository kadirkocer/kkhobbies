from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from ..auth import hash_password, verify_password, create_access_token, get_current_user
from ..db import get_session
from ..models import User
from ..schemas import LoginRequest, User as UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(
    credentials: LoginRequest,
    response: Response,
    session: Session = Depends(get_session)
):
    """Login and get access token"""
    # For single user app, get user by username or get the first user if no username provided
    if credentials.username:
        user = session.query(User).filter(User.username == credentials.username).first()
    else:
        user = session.query(User).first()  # Single user fallback
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
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
    
    return {"user": UserSchema.from_orm(user)}


@router.post("/logout")
def logout(response: Response):
    """Logout by clearing the access token cookie"""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user