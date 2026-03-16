from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoundType(str, Enum):
    PhoneScreen = "Phone Screen"
    Technical = "Technical"
    Behavioral = "Behavioral"
    Final = "Final"
    Other = "Other"


class InterviewOutcome(str, Enum):
    Pending = "Pending"
    Passed = "Passed"
    Failed = "Failed"
    Cancelled = "Cancelled"


class Interview(Base):
    __tablename__ = "interviews"
    __table_args__ = (Index("ix_interviews_application_id", "application_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"), nullable=False
    )
    round_type: Mapped[RoundType] = mapped_column(
        SQLEnum(RoundType),
        nullable=False,
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    outcome: Mapped[InterviewOutcome | None] = mapped_column(
        SQLEnum(InterviewOutcome),
        nullable=True,
        default=InterviewOutcome.Pending,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    application: Mapped["Application"] = relationship(  # noqa: F821
        "Application", back_populates="interviews"
    )
