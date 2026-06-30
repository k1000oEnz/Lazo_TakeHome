from datetime import date, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from domain import (
    AuditEntry,
    Document,
    Obligation,
    ObligationType,
    Status,
)
from domain.exceptions import ConcurrencyConflictError
from src.models import Base
from src.repository import AuditRepository, DocumentRepository, ObligationRepository


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionTesting()
    yield session
    session.close()


def make_obligation(**overrides) -> Obligation:
    defaults = {
        "id": str(uuid4()),
        "type": ObligationType.ANNUAL_REPORT,
        "title": "Test Obligation",
        "due_date": date.today() + timedelta(days=30),
        "owner": "alice@acme.com",
        "requires_document": False,
        "company_tax_id": "12-3456789",
    }
    defaults.update(overrides)
    return Obligation(**defaults)


def test_obligation_add_and_get_roundtrip(session):
    repo = ObligationRepository(session)
    obl = make_obligation(title="Annual Report 2024")
    repo.add(obl)
    session.commit()

    loaded, version = repo.get(obl.id)
    assert loaded is not None
    assert loaded.title == "Annual Report 2024"
    assert loaded.type == ObligationType.ANNUAL_REPORT
    assert loaded.status == Status.PENDING
    assert version == 1


def test_obligation_get_returns_none_for_unknown_id(session):
    repo = ObligationRepository(session)
    loaded, version = repo.get("nonexistent")
    assert loaded is None
    assert version == 0


def test_obligation_update_increments_version(session):
    repo = ObligationRepository(session)
    obl = make_obligation()
    repo.add(obl)
    session.commit()

    _, version = repo.get(obl.id)
    obl.transition_to(Status.IN_PROGRESS)
    repo.update(obl, current_version=version)
    session.commit()

    _, new_version = repo.get(obl.id)
    assert new_version == 2


def test_obligation_update_with_stale_version_raises_conflict(session):
    repo = ObligationRepository(session)
    obl = make_obligation()
    repo.add(obl)
    session.commit()

    _, current = repo.get(obl.id)
    obl.transition_to(Status.IN_PROGRESS)
    repo.update(obl, current_version=current)
    session.commit()

    obl2, _ = repo.get(obl.id)
    obl2.documents.append(Document.create(obl2.id, "report.pdf", 1024))
    obl2.transition_to(Status.SUBMITTED)
    with pytest.raises(ConcurrencyConflictError):
        repo.update(obl2, current_version=current)
    session.rollback()


def test_obligation_documents_loaded_from_relationship(session):
    obl = make_obligation(requires_document=True)
    obl_repo = ObligationRepository(session)
    obl_repo.add(obl)
    session.commit()

    doc_repo = DocumentRepository(session)
    doc_repo.add(Document.create(obl.id, "report.pdf", 1024, content=b"PDFDATA"))
    session.commit()

    loaded, _ = obl_repo.get(obl.id)
    assert loaded is not None
    assert len(loaded.documents) == 1
    assert loaded.documents[0].filename == "report.pdf"
    assert loaded.documents[0].size == 1024
    assert loaded.has_document is True


def test_audit_append_and_list(session):
    obl = make_obligation()
    obl_repo = ObligationRepository(session)
    obl_repo.add(obl)
    session.commit()

    audit_repo = AuditRepository(session)
    entry1 = AuditEntry.create(obl.id, Status.PENDING, Status.IN_PROGRESS)
    entry2 = AuditEntry.create(
        obl.id, Status.IN_PROGRESS, Status.SUBMITTED, actor="alice@acme.com"
    )
    audit_repo.append(entry1)
    audit_repo.append(entry2)
    session.commit()

    history = audit_repo.list_for_obligation(obl.id)
    assert len(history) == 2
    assert history[0].from_status == Status.PENDING
    assert history[0].to_status == Status.IN_PROGRESS
    assert history[1].actor == "alice@acme.com"


def test_audit_list_filters_by_obligation(session):
    repo = ObligationRepository(session)
    obl1 = make_obligation()
    obl2 = make_obligation()
    repo.add(obl1)
    repo.add(obl2)
    session.commit()

    audit_repo = AuditRepository(session)
    audit_repo.append(AuditEntry.create(obl1.id, Status.PENDING, Status.IN_PROGRESS))
    audit_repo.append(AuditEntry.create(obl2.id, Status.PENDING, Status.IN_PROGRESS))
    session.commit()

    history1 = audit_repo.list_for_obligation(obl1.id)
    history2 = audit_repo.list_for_obligation(obl2.id)
    assert len(history1) == 1
    assert len(history2) == 1
    assert history1[0].obligation_id == obl1.id


def test_overdue_filter_excludes_submitted_and_done(session):
    repo = ObligationRepository(session)
    overdue = make_obligation(due_date=date.today() - timedelta(days=5))
    pending_future = make_obligation(due_date=date.today() + timedelta(days=5))
    submitted_past = make_obligation(
        status=Status.SUBMITTED, due_date=date.today() - timedelta(days=5)
    )
    done_past = make_obligation(
        status=Status.DONE, due_date=date.today() - timedelta(days=5)
    )
    for o in [overdue, pending_future, submitted_past, done_past]:
        repo.add(o)
    session.commit()

    overdue_list = repo.list(overdue=True)
    ids = [o.id for o in overdue_list]
    assert overdue.id in ids
    assert pending_future.id not in ids
    assert submitted_past.id not in ids
    assert done_past.id not in ids


def test_list_orders_by_due_date_ascending(session):
    repo = ObligationRepository(session)
    far = make_obligation(title="Far", due_date=date.today() + timedelta(days=60))
    near = make_obligation(title="Near", due_date=date.today() + timedelta(days=5))
    middle = make_obligation(title="Middle", due_date=date.today() + timedelta(days=20))
    for o in [far, near, middle]:
        repo.add(o)
    session.commit()

    listed = repo.list()
    titles = [o.title for o in listed]
    assert titles == ["Near", "Middle", "Far"]


def test_status_filter_returns_only_matching(session):
    repo = ObligationRepository(session)
    pending = make_obligation(title="Pending")
    in_progress = make_obligation(title="In Progress", status=Status.IN_PROGRESS)
    for o in [pending, in_progress]:
        repo.add(o)
    session.commit()

    listed = repo.list(status=Status.PENDING)
    titles = [o.title for o in listed]
    assert titles == ["Pending"]
