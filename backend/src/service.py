from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..domain.exceptions import DomainError
from .repository import ObligationRepository
from .schemas import ObligationUpdateStatus


class ObligationService:
    def __init__(self, db: Session):
        self.repo = ObligationRepository(db)

    def change_status(self, obligation_id: str, payload: ObligationUpdateStatus):
        obligation, current_version = self.repo.get(obligation.id)
        if not obligation:
            raise HTTPException(status_code=404, detail="Obligation not found")

        obligation.has_document = payload.has_document

        try:
            if payload.status.value == "submitted":
                obligation.submit()
        except DomainError as e:
            raise HTTPException(status_code=400, detail=str(e))

        try:
            self.repo.update(obligation, current_version)
        except ValueError:
            raise HTTPException(
                status_code=409, detail="Concurrent update conflict. Try Again."
            )

        return obligation
