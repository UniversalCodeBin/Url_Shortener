import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database.base import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    short_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_short_code_active", "short_code", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<URL(id={self.id}, short_code={self.short_code})>"
