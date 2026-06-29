from datetime import datetime, timezone
from uuid import UUID

import pytest

from domain import AuditEntry, Status


def test_audit_entry_has_uuid():
    entry = AuditEntry.create(
        obligation_id="obl-1",
        from_status=Status.PENDING,
        to_status=Status.IN_PROGRESS,
    )
    UUID(entry.id)


def test_audit_entry_uses_utc_now_by_default():
    before = datetime.now(timezone.utc)
    entry = AuditEntry.create(
        obligation_id="obl-1",
        from_status=Status.PENDING,
        to_status=Status.IN_PROGRESS,
    )
    after = datetime.now(timezone.utc)
    assert before <= entry.at <= after


def test_audit_entry_accepts_explicit_timestamp():
    ts = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    entry = AuditEntry.create(
        obligation_id="obl-1",
        from_status=Status.PENDING,
        to_status=Status.IN_PROGRESS,
        at=ts,
    )
    assert entry.at == ts


def test_audit_entry_actor_is_optional():
    entry = AuditEntry.create(
        obligation_id="obl-1",
        from_status=Status.PENDING,
        to_status=Status.IN_PROGRESS,
    )
    assert entry.actor is None


def test_audit_entry_records_actor():
    entry = AuditEntry.create(
        obligation_id="obl-1",
        from_status=Status.PENDING,
        to_status=Status.IN_PROGRESS,
        actor="alice@acme.com",
    )
    assert entry.actor == "alice@acme.com"


def test_audit_entry_is_immutable():
    entry = AuditEntry.create(
        obligation_id="obl-1",
        from_status=Status.PENDING,
        to_status=Status.IN_PROGRESS,
    )
    with pytest.raises(Exception):
        entry.actor = "mallory"  # type: ignore[misc]
