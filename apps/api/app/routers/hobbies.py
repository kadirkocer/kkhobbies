
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_session
from ..models import Hobby as HobbyModel
from ..models import User
from ..schemas import Hobby, HobbyCreate, HobbyUpdate
from ..services.hobby_tree import ensure_unique_slug, get_hobby_tree, slugify

router = APIRouter(prefix="/hobbies", tags=["hobbies"])


@router.get("/", response_model=list[Hobby])
def get_hobbies(
    parent_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> list[Hobby]:
    """Get hobbies, optionally filtered by parent_id"""
    query = session.query(HobbyModel)
    if parent_id is not None:
        query = query.filter(HobbyModel.parent_id == parent_id)
    else:
        query = query.filter(HobbyModel.parent_id.is_(None))

    return query.all()


@router.get("/tree", response_model=list[Hobby])
def get_hobbies_tree(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> list[Hobby]:
    """Return hierarchical hobby tree sorted by sort_order."""
    return get_hobby_tree(session)


@router.get("/{hobby_id}", response_model=Hobby)
def get_hobby(
    hobby_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> HobbyModel:
    """Get a specific hobby including config_json"""
    hobby = session.query(HobbyModel).filter(HobbyModel.id == hobby_id).first()
    if not hobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hobby not found"
        )
    return hobby


@router.get("/{hobby_id}/children", response_model=list[Hobby])
def get_children(
    hobby_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> list[Hobby]:
    return (
        session.query(HobbyModel)
        .filter(HobbyModel.parent_id == hobby_id)
        .order_by(HobbyModel.sort_order, HobbyModel.id)
        .all()
    )


@router.post("/", response_model=Hobby)
def create_hobby(
    hobby_data: HobbyCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> HobbyModel:
    """Create a new hobby"""
    # Check if name already exists
    existing = (
        session.query(HobbyModel)
        .filter(HobbyModel.name == hobby_data.name)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hobby with this name already exists"
        )

    data = hobby_data.model_dump()
    # Slug auto-generate
    if not data.get("slug"):
        base = slugify(data["name"])
        data["slug"] = ensure_unique_slug(session, base)
    hobby = HobbyModel(**data)
    session.add(hobby)
    session.commit()
    session.refresh(hobby)
    return hobby


@router.patch("/{hobby_id}", response_model=Hobby)
def update_hobby(
    hobby_id: int,
    hobby_update: HobbyUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> HobbyModel:
    """Update a hobby"""
    hobby = session.query(HobbyModel).filter(HobbyModel.id == hobby_id).first()
    if not hobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hobby not found"
        )

    update_data = hobby_update.model_dump(exclude_unset=True)
    if "slug" in update_data and (not update_data["slug"]):
        base = slugify(update_data.get("name") or hobby.name)
        update_data["slug"] = ensure_unique_slug(session, base, exclude_id=hobby.id)

    # Check name uniqueness if updating name
    if "name" in update_data:
        existing = session.query(HobbyModel).filter(
            HobbyModel.name == update_data["name"],
            HobbyModel.id != hobby_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hobby with this name already exists"
            )

    for field, value in update_data.items():
        setattr(hobby, field, value)

    session.commit()
    session.refresh(hobby)
    return hobby


@router.delete("/{hobby_id}")
def delete_hobby(
    hobby_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Delete a hobby"""
    hobby = session.query(HobbyModel).filter(HobbyModel.id == hobby_id).first()
    if not hobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hobby not found"
        )

    session.delete(hobby)
    session.commit()
    return {"message": "Hobby deleted successfully"}
