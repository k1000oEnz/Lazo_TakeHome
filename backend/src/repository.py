from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from domain.entities import (
    AuditEntry,
    Document,
    Obligation,
    ObligationType,
    Status,
)
from domain.exceptions import ConcurrencyConflictError

from .models import AuditEntryModel, DocumentModel, ObligationModel


class ObligationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, obligation_id: str) -> tuple[Obligation | None, int]:
        model = (
            self.db.query(ObligationModel)
            .filter(ObligationModel.id == obligation_id)
            .first()
        )
        if not model:
            return None, 0
        return self._to_entity(model), model.version

    def add(self, obligation: Obligation) -> None:
        model = ObligationModel(
            id=obligation.id,
            type=obligation.type.value,
            title=obligation.title,
            description=obligation.description,
            due_date=obligation.due_date,
            owner=obligation.owner,
            requires_document=obligation.requires_document,
            status=obligation.status.value,
            company_tax_id=obligation.company_tax_id,
        )
        self.db.add(model)
        self.db.flush()

    def list(
        self,
        *,
        status: Status | None = None,
        overdue: bool | None = None,
    ) -> list[Obligation]:
        query = self.db.query(ObligationModel)
        if status is not None:
            query = query.filter(ObligationModel.status == status.value)
        if overdue is True:
            query = query.filter(
                ObligationModel.due_date < date.today(),
                ObligationModel.status.notin_(
                    [Status.SUBMITTED.value, Status.DONE.value]
                ),
            )
        models = query.order_by(ObligationModel.due_date).all()
        return [self._to_entity(m) for m in models]

    def update(self, obligation: Obligation, current_version: int) -> None:
        rows_affected = (
            self.db.query(ObligationModel)
            .filter(
                ObligationModel.id == obligation.id,
                ObligationModel.version == current_version,
            )
            .update(
                {
                    ObligationModel.status: obligation.status.value,
                    ObligationModel.version: current_version + 1,
                    ObligationModel.updated_at: datetime.now(timezone.utc),
                }
            )
        )
        if rows_affected == 0:
            raise ConcurrencyConflictError(
                f"Version conflict on obligation {obligation.id}"
            )

    def _to_entity(self, model: ObligationModel) -> Obligation:
        documents = [
            Document(
                id=d.id,
                obligation_id=d.obligation_id,
                filename=d.filename,
                size=d.size,
                content=d.content,
                uploaded_at=d.uploaded_at,
            )
            for d in model.documents
        ]
        return Obligation(
            id=model.id,
            type=ObligationType(model.type),
            title=model.title,
            description=model.description,
            due_date=model.due_date,
            owner=model.owner,
            requires_document=model.requires_document,
            company_tax_id=model.company_tax_id,
            status=Status(model.status),
            documents=documents,
        )


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def append(self, entry: AuditEntry) -> None:
        model = AuditEntryModel(
            id=entry.id,
            obligation_id=entry.obligation_id,
            from_status=entry.from_status.value,
            to_status=entry.to_status.value,
            at=entry.at,
            actor=entry.actor,
        )
        self.db.add(model)
        self.db.flush()

    def list_for_obligation(self, obligation_id: str) -> list[AuditEntry]:
        models = (
            self.db.query(AuditEntryModel)
            .filter(AuditEntryModel.obligation_id == obligation_id)
            .order_by(AuditEntryModel.at)
            .all()
        )
        return [
            AuditEntry(
                id=m.id,
                obligation_id=m.obligation_id,
                from_status=Status(m.from_status),
                to_status=Status(m.to_status),
                at=m.at,
                actor=m.actor,
            )
            for m in models
        ]


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, document: Document) -> None:
        model = DocumentModel(
            id=document.id,
            obligation_id=document.obligation_id,
            filename=document.filename,
            size=document.size,
            content=document.content,
            uploaded_at=document.uploaded_at,
        )
        self.db.add(model)
        self.db.flush()

    def list_for_obligation(self, obligation_id: str) -> list[Document]:
        models = (
            self.db.query(DocumentModel)
            .filter(DocumentModel.obligation_id == obligation_id)
            .order_by(DocumentModel.uploaded_at)
            .all()
        )
        return [
            Document(
                id=m.id,
                obligation_id=m.obligation_id,
                filename=m.filename,
                size=m.size,
                content=m.content,
                uploaded_at=m.uploaded_at,
            )
            for m in models
        ]
