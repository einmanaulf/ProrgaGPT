from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from test_models import Base

DATABASE_URL = "sqlite:///test.db"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
