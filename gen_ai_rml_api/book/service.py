from typing import Optional

from gen_ai_rml_api.book.model import Book
from gen_ai_rml_api.book.schema_model import BookModel
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


def create(db_session: Session, book: BookModel):
    """Creates a new book.

    Args:
        db_session (Session): Database session.
        book (BookModel): The book to be created.

    Returns:
        book (Book): The book created.
    """
    db_obj = Book(**book.dict())
    db_session.add(db_obj)
    return db_obj


def get_by_id(*, db_session: Session, id: int) -> Optional[Book]:
    """Returns a book.

    Args:
        db_session (Session): Database session.
        id (int): Id of the book.

    Returns:
        document (Document): Document requested.

    """
    return db_session.query(Book).filter(Book.id == id).one_or_none()


def get_all(db_session: Session):
    """Returns all books.

    Args:
        db_session (Session): Database session.

    Returns:
        books (List[Post]): All posts.
    """
    db_books = db_session.query(Book).all()
    return db_books


def update(
    *, db_session: Session, book: Book, new_book: BookModel
) -> Optional[Book]:
    """Updates a document.

    Args:
        db_session (Session): Database session.
        book (Book): The book to be updated.
        new_book (BookModel): The new book.

    Returns:
        book (Book): The book updated.
    """
    db_obj = book
    obj_data = jsonable_encoder(db_obj)
    update_data = new_book.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    db_session.add(db_obj)
    db_session.flush()
    return db_obj


def delete(*, db_session: Session, id: int):
    """Deletes a book.

    Args:
        db_session (Session): Database session.
        id (int): Id of the book.
    """
    book = db_session.query(Book).filter(Book.id == id).first()
    db_session.delete(book)
