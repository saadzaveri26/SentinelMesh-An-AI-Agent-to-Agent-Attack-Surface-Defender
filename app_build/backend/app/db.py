import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://sentinel:sentinel_dev_2026@localhost:5432/sentinelmesh")
engine = create_engine(url)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
