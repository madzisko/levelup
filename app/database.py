import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("postgresgl://ukhnjxttipiuta:9992dea7c69d2c60880bdcd604b777a2fcd3afcb91ae25d6cd1528de83992fe6@ec2-34-240-75-196.eu-west-1.compute.amazonaws.com:5432/dcbfvqtcomehuu")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
