from .events import Base
from sqlalchemy import (
    String,
    Text,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    resource: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
