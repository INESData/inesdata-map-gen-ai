from typing import Optional

from pydantic import BaseModel


class BookModel(BaseModel):
    """Pydantic schema for Book."""

    id: Optional[int]
    title: str
    description: str
    owner_id: int

    class Config:
        """Config Class."""

        orm_mode = True
