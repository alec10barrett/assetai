from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ExpenseCategory(str, Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    PROPERTY_TAX = "property_tax"
    MANAGEMENT_FEE = "management_fee"
    CAPEX = "capex"            # capital expenditure (roof, HVAC, etc.)
    LANDSCAPING = "landscaping"
    CLEANING = "cleaning"
    LEGAL_PROFESSIONAL = "legal_professional"
    MORTGAGE = "mortgage"
    OTHER = "other"


class PaymentMethod(str, Enum):
    CHECK = "check"
    ACH = "ach"
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Foreign Keys
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The document this expense was extracted from (optional — some expenses
    # will be entered manually rather than parsed from a receipt/invoice).
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # The extracted_data record that produced this expense, if any.
    # Lets you trace a verified expense all the way back to raw OCR output.
    extracted_data_id: Mapped[int | None] = mapped_column(
        ForeignKey("extracted_data.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Core Fields
    vendor: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    category: Mapped[ExpenseCategory] = mapped_column(
        SQLEnum(ExpenseCategory),
        nullable=False,
    )

    payment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        SQLEnum(PaymentMethod),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Whether a human has confirmed this record (especially important for
    # AI-extracted expenses that may need review before being trusted).
    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    property: Mapped["Property"] = relationship(
        back_populates="expenses",
    )

    document: Mapped["Document | None"] = relationship(
        foreign_keys=[document_id],
    )

    extracted_data: Mapped["ExtractedData | None"] = relationship(
        back_populates="expense",
        foreign_keys=[extracted_data_id],
    )

    def __repr__(self) -> str:
        return (
            f"<Expense(id={self.id}, vendor='{self.vendor}', "
            f"amount={self.amount}, category={self.category})>"
        )
