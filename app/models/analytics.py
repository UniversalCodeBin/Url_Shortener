import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database.base import Base


class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    url_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("urls.id"), nullable=False
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=True)
    referer: Mapped[str] = mapped_column(String(2048), nullable=True)
    country: Mapped[str] = mapped_column(String(2), nullable=True)
    city: Mapped[str] = mapped_column(String(255), nullable=True)
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_url_id_clicked_at", "url_id", "clicked_at"),
    )

    def __repr__(self) -> str:
        return f"<ClickEvent(id={self.id}, url_id={self.url_id})>"
