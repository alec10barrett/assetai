from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Property(Base):
    __tablename__ = "properties"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    state: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    zip_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    # Purchase Information
    purchase_price: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    purchase_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Optional Information
    management_company: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    expenses: Mapped[List["Expense"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan"
    )

    documents: Mapped[List["Document"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan"
    )

    events: Mapped[List["Event"]] = relationship(
    back_populates="property",
    cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Property(id={self.id}, name='{self.name}')>"
