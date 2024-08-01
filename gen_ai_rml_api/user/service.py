from typing import List, Optional

from gen_ai_rml_api.user.model import User
from gen_ai_rml_api.user.schema_model import UserModel
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


def create(db_session: Session, user: UserModel):
    """Create a user.

    Args:
        db_session (Session): Database session.
        user (UserModel): The user to be created.

    Returns:
        user (User): The user created.
    """
    db_obj = User(**user.dict())
    db_session.add(db_obj)
    return db_obj


def get_by_id(*, db_session: Session, id: int) -> Optional[User]:
    """Returns a user

    Args:
        db_session (Session): Database session.
        id (int): Id of the user.

    Returns:
        user (User): User requested.
    """
    return db_session.query(User).filter(User.id == id).one_or_none()


def get_all(db_session: Session) -> List[User]:
    """Returns all users

    Args:
        db_session (Session): Database session.

    Returns:
        users (List[User]): List of users.
    """
    db_users = db_session.query(User).all()
    return db_users


def update(
    *, db_session: Session, user: User, new_user: UserModel
) -> Optional[User]:
    """Updates a user.

    Args:
        db_session (Session): Database session.
        user (User): The user requested to be updated.
        new_user (UserModel): The new user object to be inserted.

    Returns:
        user (User): User updated.

    """
    db_obj = user
    obj_data = jsonable_encoder(db_obj)
    update_data = new_user.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    db_session.add(db_obj)
    db_session.flush()
    return db_obj


def delete(*, db_session: Session, id: int):
    """Delete user by id

    Args:
        db_session (Session): Database session.
        id (int): Id of the user.
    """
    user = db_session.query(User).filter(User.id == id).first()
    db_session.delete(user)
