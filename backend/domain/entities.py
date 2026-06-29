from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum

from .exceptions import InvalidTransitionError, MissingDocumentError


class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    DONE = "done"


class ObligationType(str, Enum):
    ANNUAL_REPORT = "annual_report"
    FRANCHISE_TAX = "franchise_tax"
    BOI_REPORT = "boi_report"
    REGISTERED_AGENT_RENEWAL = "registered_agent_renewal"


ALLOWED_TRANSITIONS: dict[Status, frozenset[Status]] = {
    Status.PENDING: frozenset({Status.IN_PROGRESS}),
    Status.IN_PROGRESS: frozenset({Status.SUBMITTED, Status.PENDING}),
    Status.SUBMITTED: frozenset({Status.DONE, Status.IN_PROGRESS}),
    Status.DONE: frozenset({Status.IN_PROGRESS}),
}


@dataclass(frozen=True)
class AuditEntry:
    id: str
    obligation_id: str
    from_status: Status
    to_status: Status
    at: datetime
    actor: str | None = None

    @staticmethod
    def create(
        obligation_id: str,
        from_status: Status,
        to_status: Status,
        *,
        actor: str | None = None,
        at: datetime | None = None,
    ) -> AuditEntry:
        return AuditEntry(
            id=str(uuid.uuid4()),
            obligation_id=obligation_id,
            from_status=from_status,
            to_status=to_status,
            at=at or datetime.now(timezone.utc),
            actor=actor,
        )


@dataclass(frozen=True)
class Document:
    id: str
    obligation_id: str
    filename: str
    size: int
    content: bytes
    uploaded_at: datetime

    @staticmethod
    def create(
        obligation_id: str,
        filename: str,
        size: int,
        *,
        content: bytes = b"",
        uploaded_at: datetime | None = None,
    ) -> Document:
        return Document(
            id=str(uuid.uuid4()),
            obligation_id=obligation_id,
            filename=filename,
            size=size,
            content=content,
            uploaded_at=uploaded_at or datetime.now(timezone.utc),
        )


@dataclass
class Obligation:
    id: str
    type: ObligationType
    title: str
    due_date: date
    owner: str
    requires_document: bool
    company_tax_id: str
    description: str | None = None
    status: Status = Status.PENDING
    documents: list[Document] = field(default_factory=list)
    version: int = 1

    @property
    def has_document(self) -> bool:
        return len(self.documents) > 0

    @property
    def is_overdue(self) -> bool:
        return self.due_date < date.today() and self.status not in (
            Status.SUBMITTED,
            Status.DONE,
        )

    @property
    def tax_id_masked(self) -> str:
        if len(self.company_tax_id) <= 4:
            return "****"
        return f"****-{self.company_tax_id[-4:]}"

    @property
    def available_transitions(self) -> list[Status]:
        return sorted(ALLOWED_TRANSITIONS[self.status], key=lambda s: s.value)

    def transition_to(
        self,
        new_status: Status,
        *,
        actor: str | None = None,
    ) -> AuditEntry:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise InvalidTransitionError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )

        if (
            new_status == Status.SUBMITTED
            and self.requires_document
            and not self.has_document
        ):
            raise MissingDocumentError(
                "Document required to mark as submitted"
            )

        from_status = self.status
        self.status = new_status

        return AuditEntry.create(
            obligation_id=self.id,
            from_status=from_status,
            to_status=new_status,
            actor=actor,
        )
