from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from domain import ObligationType, Status


class ObligationCreate(BaseModel):
    type: ObligationType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: date
    owner: str = Field(..., min_length=1, max_length=255)
    requires_document: bool
    company_tax_id: str = Field(..., min_length=1, max_length=50)


class ObligationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[date] = None
    owner: Optional[str] = Field(default=None, min_length=1, max_length=255)
    requires_document: Optional[bool] = None


class DocumentSummary(BaseModel):
    id: str
    filename: str
    size: int
    uploaded_at: datetime


class HistoryEntryResponse(BaseModel):
    id: str
    from_status: Status
    to_status: Status
    at: datetime
    actor: Optional[str] = None


class ObligationResponse(BaseModel):
    id: str
    type: ObligationType
    title: str
    description: Optional[str]
    due_date: date
    owner: str
    requires_document: bool
    status: Status
    company_tax_id: str
    is_overdue: bool
    tax_id_masked: str
    version: int

    @field_serializer("company_tax_id")
    def mask_tax_id(self, tax_id: str, _info) -> str:
        if len(tax_id) <= 4:
            return "****"
        return f"****-{tax_id[-4:]}"


class ObligationDetail(ObligationResponse):
    documents: list[DocumentSummary] = Field(default_factory=list)
    history: list[HistoryEntryResponse] = Field(default_factory=list)
    available_transitions: list[Status] = Field(default_factory=list)


class TransitionRequest(BaseModel):
    to_status: Status
    version: int = Field(..., ge=1)
    document_id: Optional[str] = None
    actor: Optional[str] = None


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None
