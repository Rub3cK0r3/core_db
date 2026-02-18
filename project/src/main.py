from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, select
from database import engine

app = FastAPI()

# Create tables if they don't exist - delete in production
SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

# The rest of endpoints on the MVP..
