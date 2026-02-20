from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from database import engine
from models.events import Event,EventResponse,EventCreate
from typing import List

app = FastAPI()

# Crear tablas (solo desarrollo)
SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session

# GET without ID parameter => lists all of them
@app.get("/v1/events", response_model=List[EventResponse])
def list_events(db: Session = Depends(get_db)):
    statement = select(Event)
    events = db.exec(statement).all()
    return events

# GET with ID => list the event that has that ID
@app.get("/v1/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    statement = select(Event).where(Event.id == event_id)
    event = db.exec(statement).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event

# POST => It just adds the given event
@app.post("/v1/events", response_model=EventResponse)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    db.add(Event(**payload.dict()))
    db.commit()
    db.refresh(payload)
    return payload
