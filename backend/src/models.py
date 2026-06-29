import uuid

from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ObligationModel(Base):
    __tablename__ = "obligations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    owner = Column(String, nullable=False)
    requires_document = Column(Boolean, nullable=False, default=False)
    has_document = Column(Boolean, nullable=False, default=False)
    status = Column(String, nullable=False, default="pending")

    company_tax_id = Column(String, nullable=False)

    version = Column(Integer, nullable=False, default=1)
