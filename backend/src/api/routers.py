from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi import status as http_status
from sqlalchemy.orm import Session

from domain import Status

from src.database import get_db

from .mapping import to_obligation_detail, to_obligation_response
from .schemas import (
    DocumentSummary,
    HistoryEntryResponse,
    ObligationCreate,
    ObligationDetail,
    ObligationResponse,
    ObligationUpdate,
    TransitionRequest,
)
from .service import ObligationService

router = APIRouter(prefix="/api/obligations", tags=["obligations"])


@router.get("", response_model=list[ObligationResponse])
def list_obligations(
    status: Optional[Status] = Query(default=None),
    overdue: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ObligationResponse]:
    service = ObligationService(db)
    obligations = service.list_obligations(status=status, overdue=overdue)
    return [to_obligation_response(o) for o in obligations]


@router.post(
    "",
    response_model=ObligationDetail,
    status_code=http_status.HTTP_201_CREATED,
)
def create_obligation(
    payload: ObligationCreate,
    db: Session = Depends(get_db),
) -> ObligationDetail:
    service = ObligationService(db)
    obligation = service.create_obligation(**payload.model_dump())
    return to_obligation_detail(obligation, history=[])


@router.get("/{obligation_id}", response_model=ObligationDetail)
def get_obligation(
    obligation_id: str,
    db: Session = Depends(get_db),
) -> ObligationDetail:
    service = ObligationService(db)
    obligation = service.get_obligation(obligation_id)
    history = service.get_history(obligation_id)
    return to_obligation_detail(obligation, history=history)


@router.patch("/{obligation_id}", response_model=ObligationDetail)
def update_obligation(
    obligation_id: str,
    payload: ObligationUpdate,
    db: Session = Depends(get_db),
) -> ObligationDetail:
    service = ObligationService(db)
    obligation = service.update_obligation(
        obligation_id, **payload.model_dump(exclude_unset=True)
    )
    history = service.get_history(obligation_id)
    return to_obligation_detail(obligation, history=history)


@router.get(
    "/{obligation_id}/history", response_model=list[HistoryEntryResponse]
)
def get_history(
    obligation_id: str,
    db: Session = Depends(get_db),
) -> list[HistoryEntryResponse]:
    service = ObligationService(db)
    history = service.get_history(obligation_id)
    from .mapping import to_history_entry
    return [to_history_entry(h) for h in history]


transitions_router = APIRouter(prefix="/api/obligations", tags=["transitions"])


@transitions_router.post(
    "/{obligation_id}/transitions", response_model=ObligationDetail
)
def post_transition(
    obligation_id: str,
    payload: TransitionRequest,
    db: Session = Depends(get_db),
) -> ObligationDetail:
    service = ObligationService(db)
    obligation = service.transition(
        obligation_id,
        to_status=payload.to_status,
        version=payload.version,
        actor=payload.actor,
        document_id=payload.document_id,
    )
    history = service.get_history(obligation_id)
    return to_obligation_detail(obligation, history=history)


documents_router = APIRouter(prefix="/api/obligations", tags=["documents"])


@documents_router.post(
    "/{obligation_id}/documents",
    response_model=DocumentSummary,
    status_code=http_status.HTTP_201_CREATED,
)
async def upload_document(
    obligation_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentSummary:
    service = ObligationService(db)
    content = await file.read()
    document = service.attach_document(
        obligation_id,
        filename=file.filename or "unnamed",
        content=content,
    )
    from .mapping import to_document_summary
    return to_document_summary(document)
