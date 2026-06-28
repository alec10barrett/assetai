from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class EventType(str, Enum):
    PROPERTY_CREATED = "property_created"

    DOCUMENT_UPLOADED = "document_uploaded"

    EXPENSE_RECORDED = "expense_recorded"

    MAINTENANCE_COMPLETED = "maintenance_completed"

    INSPECTION_COMPLETED = "inspection_completed"

    PROPERTY_NOTE = "property_note"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )

    event_type: Mapped[EventType] = mapped_column(
        SQLEnum(EventType),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    event_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    property: Mapped["Property"] = relationship(
        back_populates="events"
    )

    document: Mapped["Document"] = relationship(
        back_populates="events"
    )

    def __repr__(self) -> str:
        return (
            f"<Event(id={self.id}, "
            f"type={self.event_type}, "
            f"title='{self.title}')>"
        )
