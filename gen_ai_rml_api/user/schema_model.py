from typing import Optional

from pydantic import BaseModel


class UserModel(BaseModel):
    """Pydantic schema for User."""

    id: Optional[int]
    name: str
    email: str
    hashed_password: str

    class Config:
        """Config Class."""

        orm_mode = True
