from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_serializer


class ObligationType(str, Enum):
    ANNUAL_REPORT = "annual_report"
    FRANCHISE_TAX = "franchise_tax"
    BOI_REPORT = "boi_report"
    REGISTERED_AGENT_RENEWAL = "registered_agent_renewal"


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    DONE = "done"


class ObligationBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: ObligationType
    due_date: date
    owner: str = Field(..., description="Mandatory Owner")
    requires_document: bool
    company_tax_id: str = Field(..., description="Sensitive Data")


# POST
class ObligationCreate(ObligationBase):
    pass


# PATCH
class ObligationUpdateStatus(BaseModel):
    status: Status
    has_document: bool = False


# GET
class ObligationResponse(ObligationBase):
    id: str
    status: Status
    has_document: bool
    is_overdue: bool

    @field_serializer("company_tax_id")
    def mask_tasx_id(self, tax_id: str, _info):
        if len(tax_id) <= 4:
            return "****"
        return f"****-{tax_id[-4:]}"
