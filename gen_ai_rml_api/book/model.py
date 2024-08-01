from gen_ai_rml_api.database.connection import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="book")
