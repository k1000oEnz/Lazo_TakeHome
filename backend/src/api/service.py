from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from domain import (
    AuditEntry,
    Document,
    NotFoundError,
    Obligation,
    ObligationType,
    Status,
)

from src.repository import AuditRepository, DocumentRepository, ObligationRepository


class ObligationService:
    def __init__(self, db: Session):
        self.db = db
        self.obligation_repo = ObligationRepository(db)
        self.audit_repo = AuditRepository(db)
        self.document_repo = DocumentRepository(db)

    def list_obligations(
        self,
        *,
        status: Optional[Status] = None,
        overdue: Optional[bool] = None,
    ) -> list[Obligation]:
        return self.obligation_repo.list(status=status, overdue=overdue)

    def get_obligation(self, obligation_id: str) -> Obligation:
        obligation, _ = self.obligation_repo.get(obligation_id)
        if not obligation:
            raise NotFoundError(f"Obligation {obligation_id} not found")
        return obligation

    def get_history(self, obligation_id: str) -> list[AuditEntry]:
        self.get_obligation(obligation_id)
        return self.audit_repo.list_for_obligation(obligation_id)

    def create_obligation(
        self,
        *,
        type: ObligationType,
        title: str,
        description: Optional[str],
        due_date: date,
        owner: str,
        requires_document: bool,
        company_tax_id: str,
    ) -> Obligation:
        obligation = Obligation(
            id=str(uuid.uuid4()),
            type=type,
            title=title,
            description=description,
            due_date=due_date,
            owner=owner,
            requires_document=requires_document,
            company_tax_id=company_tax_id,
        )
        self.obligation_repo.add(obligation)
        self.db.commit()
        return obligation

    def update_obligation(
        self,
        obligation_id: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[date] = None,
        owner: Optional[str] = None,
        requires_document: Optional[bool] = None,
    ) -> Obligation:
        obligation, version = self.obligation_repo.get(obligation_id)
        if not obligation:
            raise NotFoundError(f"Obligation {obligation_id} not found")

        if title is not None:
            obligation.title = title
        if description is not None:
            obligation.description = description
        if due_date is not None:
            obligation.due_date = due_date
        if owner is not None:
            obligation.owner = owner
        if requires_document is not None:
            obligation.requires_document = requires_document

        self.obligation_repo.update(obligation, current_version=version)
        self.db.commit()
        return obligation

    def transition(
        self,
        obligation_id: str,
        *,
        to_status: Status,
        version: int,
        actor: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> Obligation:
        obligation, current_version = self.obligation_repo.get(obligation_id)
        if not obligation:
            raise NotFoundError(f"Obligation {obligation_id} not found")

        if current_version != version:
            from domain import ConcurrencyConflictError

            raise ConcurrencyConflictError(
                f"Version mismatch on obligation {obligation_id}"
            )

        if document_id is not None:
            document = self.document_repo.get(document_id)
            if document is None or document.obligation_id != obligation_id:
                raise NotFoundError(
                    f"Document {document_id} not found for this obligation"
                )
            if document not in obligation.documents:
                obligation.documents.append(document)

        audit = obligation.transition_to(to_status, actor=actor)
        self.obligation_repo.update(obligation, current_version=current_version)
        self.audit_repo.append(audit)
        self.db.commit()
        return obligation

    def attach_document(
        self,
        obligation_id: str,
        *,
        filename: str,
        content: bytes,
    ) -> Document:
        self.get_obligation(obligation_id)
        document = Document.create(
            obligation_id=obligation_id,
            filename=filename,
            size=len(content),
            content=content,
        )
        self.document_repo.add(document)
        self.db.commit()
        return document
