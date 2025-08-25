from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_session
from ..models import User as UserModel
from ..schemas import User, UserUpdate
from ..services.uploads import public_url, store_avatar

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
def get_current_user_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.patch("/me", response_model=User)
def update_current_user(
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Update current user profile"""
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    session.commit()
    session.refresh(current_user)
    return current_user


@router.post("/me/avatar", response_model=User)
async def upload_avatar(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    info = await store_avatar(file)
    current_user.avatar_path = public_url(info["file_path"])  # store public URL
    session.commit()
    session.refresh(current_user)
    return current_user
