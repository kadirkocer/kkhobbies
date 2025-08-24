from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..auth import get_current_user
from ..db import get_session
from ..models import User, HobbyType as HobbyTypeModel
from ..schemas import HobbyType, HobbyTypeCreate, HobbyTypeUpdate
from ..services.schema_validation import is_valid_json_schema

router = APIRouter(prefix="/hobby-types", tags=["hobby-types"])




@router.get("/", response_model=List[HobbyType])
def get_hobby_types(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all hobby types"""
    return session.query(HobbyTypeModel).all()


@router.post("/", response_model=HobbyType)
def create_hobby_type(
    hobby_type_data: HobbyTypeCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new hobby type"""
    # Validate JSON Schema
    if not is_valid_json_schema(hobby_type_data.schema_json):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON Schema"
        )
    
    # Check if key already exists
    existing = session.query(HobbyTypeModel).filter(HobbyTypeModel.key == hobby_type_data.key).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hobby type with this key already exists"
        )
    
    hobby_type = HobbyTypeModel(**hobby_type_data.model_dump())
    session.add(hobby_type)
    session.commit()
    session.refresh(hobby_type)
    return hobby_type


@router.patch("/{key}", response_model=HobbyType)
def update_hobby_type(
    key: str,
    hobby_type_update: HobbyTypeUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a hobby type"""
    hobby_type = session.query(HobbyTypeModel).filter(HobbyTypeModel.key == key).first()
    if not hobby_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hobby type not found"
        )
    
    update_data = hobby_type_update.model_dump(exclude_unset=True)
    
    # Validate JSON Schema if provided
    if "schema_json" in update_data:
        if not is_valid_json_schema(update_data["schema_json"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON Schema"
            )
    
    for field, value in update_data.items():
        setattr(hobby_type, field, value)
    
    session.commit()
    session.refresh(hobby_type)
    return hobby_type


@router.delete("/{key}")
def delete_hobby_type(
    key: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a hobby type"""
    hobby_type = session.query(HobbyTypeModel).filter(HobbyTypeModel.key == key).first()
    if not hobby_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hobby type not found"
        )
    
    session.delete(hobby_type)
    session.commit()
    return {"message": "Hobby type deleted successfully"}