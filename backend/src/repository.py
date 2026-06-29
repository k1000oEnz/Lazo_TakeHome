from sqlalchemy.orm import Session
from .models import ObligationModel
from ..domain.entities import Obligation, Status

class ObligationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, obligation_id: str) -> tuple[Obligation | None, int]:
        model = self.db.query(ObligationModel).filter(ObligationModel.id == obligation_id).first()
        if not model:
            return None, 0

        oblgation = Obligation(
            id=model.id,
            title= model.title,
            due_date= model.due_date,
            requires_document= model.requires_document,
            status = Status(model.status),
            has_document= model.has_document
        )

        return oblgation, model.version

    def update(self, obligation: Obligation, current_version: int):
        rows_affected = self.db.query(ObligationModel).filter(
            ObligationModel.id == obligation.id,
            ObligationModel.version == current_version
        ).update({
            "status": obligation.status.value,
            "has_document": obligation.has_document,
            "version": current_version + 1
        })

        if rows_affected == 0:
            raise ValueError("Concurrency conflict")

        self.db.commit()
