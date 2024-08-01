from gen_ai_rml_api.database.connection import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


# SQLAlchemy Model
class User(Base):
    """User."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationships
    posts = relationship("Book", back_populates="owner")
