from __future__ import annotations

from domain import AuditEntry, Document, Obligation

from .schemas import (
    DocumentSummary,
    HistoryEntryResponse,
    ObligationDetail,
    ObligationResponse,
)


def to_obligation_response(obligation: Obligation) -> ObligationResponse:
    return ObligationResponse(
        id=obligation.id,
        type=obligation.type,
        title=obligation.title,
        description=obligation.description,
        due_date=obligation.due_date,
        owner=obligation.owner,
        requires_document=obligation.requires_document,
        status=obligation.status,
        company_tax_id=obligation.company_tax_id,
        is_overdue=obligation.is_overdue,
        tax_id_masked=obligation.tax_id_masked,
        version=obligation.version,
    )


def to_document_summary(document: Document) -> DocumentSummary:
    return DocumentSummary(
        id=document.id,
        filename=document.filename,
        size=document.size,
        uploaded_at=document.uploaded_at,
    )


def to_history_entry(entry: AuditEntry) -> HistoryEntryResponse:
    return HistoryEntryResponse(
        id=entry.id,
        from_status=entry.from_status,
        to_status=entry.to_status,
        at=entry.at,
        actor=entry.actor,
    )


def to_obligation_detail(
    obligation: Obligation,
    *,
    history: list[AuditEntry],
) -> ObligationDetail:
    return ObligationDetail(
        id=obligation.id,
        type=obligation.type,
        title=obligation.title,
        description=obligation.description,
        due_date=obligation.due_date,
        owner=obligation.owner,
        requires_document=obligation.requires_document,
        status=obligation.status,
        company_tax_id=obligation.company_tax_id,
        is_overdue=obligation.is_overdue,
        tax_id_masked=obligation.tax_id_masked,
        version=obligation.version,
        documents=[to_document_summary(d) for d in obligation.documents],
        history=[to_history_entry(h) for h in history],
        available_transitions=obligation.available_transitions,
    )
