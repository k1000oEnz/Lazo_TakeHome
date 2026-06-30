from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class ObligationModel(Base):
    __tablename__ = "obligations"

    id: Mapped[str] = mapped_column(primary_key=True, default=_new_uuid)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    due_date: Mapped[date] = mapped_column(nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    requires_document: Mapped[bool] = mapped_column(default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )
    company_tax_id: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )

    documents: Mapped[list[DocumentModel]] = relationship(
        back_populates="obligation",
        cascade="all, delete-orphan",
        order_by="DocumentModel.uploaded_at",
    )
    audit_entries: Mapped[list[AuditEntryModel]] = relationship(
        back_populates="obligation",
        cascade="all, delete-orphan",
        order_by="AuditEntryModel.at",
    )


class AuditEntryModel(Base):
    __tablename__ = "audit_entries"

    id: Mapped[str] = mapped_column(primary_key=True, default=_new_uuid)
    obligation_id: Mapped[str] = mapped_column(
        ForeignKey("obligations.id"), nullable=False, index=True
    )
    from_status: Mapped[str] = mapped_column(String(20), nullable=False)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    at: Mapped[datetime] = mapped_column(nullable=False)
    actor: Mapped[str | None] = mapped_column(String(255), nullable=True)

    obligation: Mapped[ObligationModel] = relationship(back_populates="audit_entries")


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(primary_key=True, default=_new_uuid)
    obligation_id: Mapped[str] = mapped_column(
        ForeignKey("obligations.id"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)

    obligation: Mapped[ObligationModel] = relationship(back_populates="documents")
