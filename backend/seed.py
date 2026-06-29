import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from domain import ObligationType, Status
from src.database import SessionLocal, init_db
from src.models import ObligationModel

SAMPLES = [
    {
        "id": "obl-1",
        "type": ObligationType.ANNUAL_REPORT.value,
        "title": "Annual Report 2024",
        "description": "State of Delaware annual filing",
        "due_date": date.today() + timedelta(days=15),
        "owner": "alice@acme.com",
        "status": Status.PENDING.value,
        "requires_document": True,
        "company_tax_id": "12-3456789",
    },
    {
        "id": "obl-2",
        "type": ObligationType.FRANCHISE_TAX.value,
        "title": "Delaware Franchise Tax",
        "due_date": date.today() - timedelta(days=3),
        "owner": "bob@acme.com",
        "status": Status.IN_PROGRESS.value,
        "requires_document": True,
        "company_tax_id": "12-3456789",
    },
    {
        "id": "obl-3",
        "type": ObligationType.BOI_REPORT.value,
        "title": "Beneficial Ownership Report",
        "due_date": date.today() + timedelta(days=60),
        "owner": "alice@acme.com",
        "status": Status.PENDING.value,
        "requires_document": False,
        "company_tax_id": "12-3456789",
    },
    {
        "id": "obl-4",
        "type": ObligationType.REGISTERED_AGENT_RENEWAL.value,
        "title": "Registered Agent Renewal",
        "due_date": date.today() - timedelta(days=10),
        "owner": "carol@acme.com",
        "status": Status.SUBMITTED.value,
        "requires_document": True,
        "company_tax_id": "12-3456789",
    },
    {
        "id": "obl-5",
        "type": ObligationType.ANNUAL_REPORT.value,
        "title": "Annual Report 2023",
        "due_date": date.today() - timedelta(days=180),
        "owner": "alice@acme.com",
        "status": Status.DONE.value,
        "requires_document": True,
        "company_tax_id": "12-3456789",
    },
]


def main() -> None:
    init_db()
    with SessionLocal() as session:
        if session.query(ObligationModel).count() > 0:
            print("Already seeded, skipping")
            return
        for sample in SAMPLES:
            session.add(ObligationModel(**sample, version=1))
        session.commit()
    print(f"Seeded {len(SAMPLES)} obligations")


if __name__ == "__main__":
    main()
