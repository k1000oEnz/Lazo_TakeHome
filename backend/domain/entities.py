from dataclasses import dataclass
from datetime import date
from enum import Enum

from .exceptions import InvalidTransitionError, MissingDocumentError


class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    DONE = "done"


@dataclass
class Obligation:
    id: str
    title: str
    due_date: date
    requires_document: bool
    status: Status = Status.PENDING
    has_document: bool = False

    @property
    def is_overdue(self) -> bool:
        return date.today() > self.due_date and self.status not in (
            Status.SUBMITTED,
            Status.DONE,
        )

    def submit(self):
        if self.status != Status.IN_PROGRESS:
            raise InvalidTransitionError(
                "Should be in_progress to change into submitted"
            )

        if self.requires_document and not self.has_document:
            raise MissingDocumentError(
                "Transaction blocked: attached document required"
            )

        self.status = Status.SUBMITTED
