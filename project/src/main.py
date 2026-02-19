from fastapi import FastAPI
from sqlmodel import SQLModel, Session
from database import engine

app = FastAPI()

# Create tables if they don't exist - delete in production
SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

# TODOS:
# The rest of endpoints on the MVP..

# Make class implementation for a `data Collector`

# Make class implementation for a `data Processor`

# Make the CLI based alert system
# with logs and audit store
