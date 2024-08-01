from http import HTTPStatus
from typing import List

from gen_ai_rml_api.database.connection import get_db
from gen_ai_rml_api.user.schema_model import UserModel
from gen_ai_rml_api.user.service import create as create_user
from gen_ai_rml_api.user.service import delete as delete_user
from gen_ai_rml_api.user.service import get_all as get_all_users
from gen_ai_rml_api.user.service import get_by_id as get_user_by_id
from gen_ai_rml_api.user.service import update as update_user
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=UserModel
)
def create(user: UserModel, db: Session = Depends(get_db)):
    """Create a new user."""
    user = create_user(db_session=db, user=user)
    db.commit()
    return user


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=UserModel)
def get_by_id(id, db: Session = Depends(get_db)):
    """Get one user."""
    user = get_user_by_id(db_session=db, id=id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value, detail="User not found"
        )
    return user


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[UserModel]
)
def get_all(db: Session = Depends(get_db)):
    """Get all users."""
    return get_all_users(db_session=db)


@router.put(
    "/update/{id}", status_code=status.HTTP_200_OK, response_model=UserModel
)
def update(new_user: UserModel, user_id: int, db: Session = Depends(get_db)):
    """Update one user."""
    user = get_user_by_id(db_session=db, id=user_id)
    updated_user = update_user(db_session=db, new_user=new_user, user=user)
    db.commit()
    return updated_user


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id, db: Session = Depends(get_db)):
    """Delete one user."""
    delete_user(db_session=db, id=id)
    db.commit()
    return Response(status_code=HTTPStatus.NO_CONTENT.value)
