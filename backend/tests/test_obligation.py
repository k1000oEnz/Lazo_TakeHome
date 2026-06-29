from datetime import date, timedelta
from uuid import uuid4

import pytest

from domain import (
    Document,
    InvalidTransitionError,
    MissingDocumentError,
    Obligation,
    ObligationType,
    Status,
)


def make_obligation(**overrides) -> Obligation:
    defaults = {
        "id": str(uuid4()),
        "type": ObligationType.ANNUAL_REPORT,
        "title": "Annual Report 2024",
        "due_date": date.today() + timedelta(days=30),
        "owner": "alice@acme.com",
        "requires_document": False,
        "company_tax_id": "12-3456789",
    }
    defaults.update(overrides)
    return Obligation(**defaults)


def test_pending_to_in_progress_is_allowed():
    obl = make_obligation()
    audit = obl.transition_to(Status.IN_PROGRESS)
    assert obl.status == Status.IN_PROGRESS
    assert audit.from_status == Status.PENDING
    assert audit.to_status == Status.IN_PROGRESS


def test_in_progress_to_submitted_is_allowed():
    obl = make_obligation(status=Status.IN_PROGRESS)
    audit = obl.transition_to(Status.SUBMITTED)
    assert obl.status == Status.SUBMITTED
    assert audit.from_status == Status.IN_PROGRESS
    assert audit.to_status == Status.SUBMITTED


def test_in_progress_to_pending_is_allowed():
    obl = make_obligation(status=Status.IN_PROGRESS)
    obl.transition_to(Status.PENDING)
    assert obl.status == Status.PENDING


def test_submitted_to_done_is_allowed():
    obl = make_obligation(status=Status.SUBMITTED)
    obl.transition_to(Status.DONE)
    assert obl.status == Status.DONE


def test_submitted_to_in_progress_is_allowed():
    obl = make_obligation(status=Status.SUBMITTED)
    obl.transition_to(Status.IN_PROGRESS)
    assert obl.status == Status.IN_PROGRESS


def test_done_to_in_progress_is_allowed():
    obl = make_obligation(status=Status.DONE)
    obl.transition_to(Status.IN_PROGRESS)
    assert obl.status == Status.IN_PROGRESS


def test_pending_to_submitted_is_rejected():
    obl = make_obligation()
    with pytest.raises(InvalidTransitionError):
        obl.transition_to(Status.SUBMITTED)


def test_pending_to_done_is_rejected():
    obl = make_obligation()
    with pytest.raises(InvalidTransitionError):
        obl.transition_to(Status.DONE)


def test_in_progress_to_done_is_rejected():
    obl = make_obligation(status=Status.IN_PROGRESS)
    with pytest.raises(InvalidTransitionError):
        obl.transition_to(Status.DONE)


def test_submitted_to_pending_is_rejected():
    obl = make_obligation(status=Status.SUBMITTED)
    with pytest.raises(InvalidTransitionError):
        obl.transition_to(Status.PENDING)


def test_done_to_pending_is_rejected():
    obl = make_obligation(status=Status.DONE)
    with pytest.raises(InvalidTransitionError):
        obl.transition_to(Status.PENDING)


def test_done_to_submitted_is_rejected():
    obl = make_obligation(status=Status.DONE)
    with pytest.raises(InvalidTransitionError):
        obl.transition_to(Status.SUBMITTED)


def test_self_transition_is_rejected():
    obl = make_obligation()
    with pytest.raises(InvalidTransitionError):
        obl.transition_to(Status.PENDING)


def test_submitted_without_required_doc_is_rejected():
    obl = make_obligation(
        status=Status.IN_PROGRESS,
        requires_document=True,
    )
    with pytest.raises(MissingDocumentError):
        obl.transition_to(Status.SUBMITTED)


def test_submitted_with_required_doc_is_allowed():
    obl = make_obligation(
        status=Status.IN_PROGRESS,
        requires_document=True,
    )
    obl.documents.append(Document.create(obl.id, "report.pdf", 1024))
    obl.transition_to(Status.SUBMITTED)
    assert obl.status == Status.SUBMITTED


def test_submitted_without_doc_when_not_required_is_allowed():
    obl = make_obligation(
        status=Status.IN_PROGRESS,
        requires_document=False,
    )
    obl.transition_to(Status.SUBMITTED)
    assert obl.status == Status.SUBMITTED


def test_has_document_reflects_documents_list():
    obl = make_obligation(requires_document=True)
    assert not obl.has_document
    obl.documents.append(Document.create(obl.id, "report.pdf", 1024))
    assert obl.has_document


def test_pending_with_past_due_is_overdue():
    obl = make_obligation(
        status=Status.PENDING,
        due_date=date.today() - timedelta(days=1),
    )
    assert obl.is_overdue


def test_in_progress_with_past_due_is_overdue():
    obl = make_obligation(
        status=Status.IN_PROGRESS,
        due_date=date.today() - timedelta(days=1),
    )
    assert obl.is_overdue


def test_submitted_with_past_due_is_not_overdue():
    obl = make_obligation(
        status=Status.SUBMITTED,
        due_date=date.today() - timedelta(days=1),
    )
    assert not obl.is_overdue


def test_done_with_past_due_is_not_overdue():
    obl = make_obligation(
        status=Status.DONE,
        due_date=date.today() - timedelta(days=1),
    )
    assert not obl.is_overdue


def test_pending_with_future_due_is_not_overdue():
    obl = make_obligation(
        status=Status.PENDING,
        due_date=date.today() + timedelta(days=30),
    )
    assert not obl.is_overdue


def test_due_today_is_not_overdue():
    obl = make_obligation(due_date=date.today())
    assert not obl.is_overdue


def test_tax_id_masked_shows_last_four():
    obl = make_obligation(company_tax_id="12-3456789")
    assert obl.tax_id_masked == "****-6789"


def test_tax_id_masked_short_value_fully_masked():
    obl = make_obligation(company_tax_id="1234")
    assert obl.tax_id_masked == "****"


def test_tax_id_masked_very_short_value_fully_masked():
    obl = make_obligation(company_tax_id="12")
    assert obl.tax_id_masked == "****"
