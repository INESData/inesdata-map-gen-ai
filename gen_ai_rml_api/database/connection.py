from gen_ai_rml_api.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """Returns session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
