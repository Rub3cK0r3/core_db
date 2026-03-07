from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import os

from models.models import User, Event, Alert
from models.schemas import EventResponse, EventCreate
from models.base import Base
from core.logs.logging_module.main import Logger

# --- Load environment variables ---
load_dotenv()

# Database URL, JWT secret key, algorithm, and token expiry
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://devuser:devpass@db:5432/coredb")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALERT_SEVERITIES = {"error", "fatal"}

# --- Initialize FastAPI + logger ---
app = FastAPI()
audit_logger = Logger()

# --- SQLAlchemy engine + session setup ---
engine = create_engine(DATABASE_URL, echo=True, future=True)

def get_db():
    """Dependency: returns a database session and closes it automatically."""
    with Session(engine) as session:
        yield session

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that the provided password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Fetch a user from the database by username."""
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalars().first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with an optional expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency that returns the currently authenticated user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.
    Request: form data with username and password
    Response: access_token and token_type
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        audit_logger.warning(f"AUTH_FAIL username={form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    audit_logger.info(f"AUTH_SUCCESS username={user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/v1/events", response_model=List[EventResponse])
def list_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Event)
    events = db.execute(stmt).scalars().all()
    audit_logger.info(f"LIST_EVENTS username={current_user.username} count={len(events)}")
    return events

@app.get("/v1/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Event).where(Event.id == event_id)
    event = db.execute(stmt).scalars().first()
    if not event:
        audit_logger.warning(f"GET_EVENT_NOT_FOUND username={current_user.username} event_id={event_id}")
        raise HTTPException(status_code=404, detail="Event not found")
    audit_logger.info(f"GET_EVENT username={current_user.username} event_id={event_id}")
    return event

@app.post("/v1/events", response_model=EventResponse)
def create_event(payload: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = Event(**payload.model_dump())
    db.add(event)
    # Simple inline alerting: persist critical events into alerts table
    if event.severity in ALERT_SEVERITIES:
        alert = Alert(
            id=event.id,
            severity=event.severity,
            resource=event.resource,
            payload=payload.model_dump(),
            created_at=event.received_at or event.timestamp,
        )
        db.add(alert)

    db.commit()
    db.refresh(event)
    audit_logger.info(f"CREATE_EVENT username={current_user.username} event_id={event.id} severity={event.severity}")
    return event

# --- Create database tables (development only) ---
Base.metadata.create_all(engine)
