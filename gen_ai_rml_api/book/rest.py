from http import HTTPStatus
from typing import List

from gen_ai_rml_api.book.schema_model import BookModel
from gen_ai_rml_api.book.service import create as create_book
from gen_ai_rml_api.book.service import delete as delete_book
from gen_ai_rml_api.book.service import get_all as get_all_books
from gen_ai_rml_api.book.service import get_by_id as get_book_by_id
from gen_ai_rml_api.book.service import update as update_post
from gen_ai_rml_api.database.connection import get_db
from gen_ai_rml_api.logs import logger as logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

logger = logging.get_logger(__name__)

router = APIRouter()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=BookModel
)
def create(book: BookModel, db: Session = Depends(get_db)):
    """Create a new book."""
    post = create_book(db_session=db, book=book)
    db.commit()
    logger.info(f"Created book with id: {post.id}")
    return post


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[BookModel]
)
def get_all(db: Session = Depends(get_db)):
    """Get all books."""
    return get_all_books(db_session=db)


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=BookModel)
def get_by_id(id, db: Session = Depends(get_db)):
    """Get one book."""
    book = get_book_by_id(db_session=db, id=id)
    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value, detail="Book not found"
        )
    return book


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id, db: Session = Depends(get_db)):
    """Delete one post."""
    delete_book(db_session=db, id=id)
    db.commit()
    return Response(status_code=HTTPStatus.NO_CONTENT.value)


@router.put(
    "/update/{id}", status_code=status.HTTP_200_OK, response_model=BookModel
)
def update(new_book: BookModel, book_id: int, db: Session = Depends(get_db)):
    """Update one user."""
    book = get_book_by_id(db_session=db, id=id)
    updated_post = update_post(db_session=db, new_book=new_book, book=book)
    db.commit()
    return updated_post
