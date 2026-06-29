import uuid
from datetime import date

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ObligationModel(Base):
    __tablename__ = "obligations"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str]
    description: Mapped[str | None]
    type: Mapped[str]
    due_date: Mapped[date]
    owner: Mapped[str]
    requires_document: Mapped[bool] = mapped_column(default=False)
    has_document: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(default="pending")

    company_tax_id: Mapped[str]

    version: Mapped[int] = mapped_column(default=1)
