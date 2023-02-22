from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://klaus:password@localhost:5432/immomio"

engine = create_engine(
    DATABASE_URL, echo=True
)
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()