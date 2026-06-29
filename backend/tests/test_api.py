from __future__ import annotations

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.database import get_db
from src.models import Base


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = SessionTesting()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def make_payload(**overrides) -> dict:
    defaults = {
        "type": "annual_report",
        "title": "Annual Report 2024",
        "description": "State of Delaware annual filing",
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "owner": "alice@acme.com",
        "requires_document": True,
        "company_tax_id": "12-3456789",
    }
    defaults.update(overrides)
    return defaults


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_obligation_returns_masked_tax_id(client):
    response = client.post("/api/obligations", json=make_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Annual Report 2024"
    assert data["status"] == "pending"
    assert data["company_tax_id"] == "****-6789"
    assert data["tax_id_masked"] == "****-6789"
    assert data["is_overdue"] is False
    assert data["version"] == 1
    assert data["available_transitions"] == ["in_progress"]
    assert data["history"] == []


def test_get_obligation_returns_history_and_documents(client):
    create = client.post("/api/obligations", json=make_payload())
    obl_id = create.json()["id"]

    transition = client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "in_progress", "version": 1, "actor": "alice"},
    )
    assert transition.status_code == 200

    response = client.get(f"/api/obligations/{obl_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["version"] == 2
    assert data["available_transitions"] == ["pending", "submitted"]
    assert len(data["history"]) == 1
    assert data["history"][0]["from_status"] == "pending"
    assert data["history"][0]["to_status"] == "in_progress"
    assert data["history"][0]["actor"] == "alice"


def test_get_nonexistent_returns_404_with_code(client):
    response = client.get("/api/obligations/nonexistent")
    assert response.status_code == 404
    assert response.json() == {
        "code": "NOT_FOUND",
        "message": "Obligation nonexistent not found",
    }


def test_list_obligations_returns_array(client):
    client.post("/api/obligations", json=make_payload(title="A"))
    client.post("/api/obligations", json=make_payload(title="B"))

    response = client.get("/api/obligations")
    assert response.status_code == 200
    titles = [o["title"] for o in response.json()]
    assert sorted(titles) == ["A", "B"]


def test_list_obligations_filters_by_overdue(client):
    client.post(
        "/api/obligations",
        json=make_payload(
            title="Past Due",
            due_date=(date.today() - timedelta(days=5)).isoformat(),
        ),
    )
    client.post(
        "/api/obligations",
        json=make_payload(
            title="Future Due",
            due_date=(date.today() + timedelta(days=30)).isoformat(),
        ),
    )

    response = client.get("/api/obligations?overdue=true")
    assert response.status_code == 200
    titles = [o["title"] for o in response.json()]
    assert titles == ["Past Due"]


def test_invalid_transition_returns_400_with_code(client):
    create = client.post("/api/obligations", json=make_payload())
    obl_id = create.json()["id"]

    response = client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "done", "version": 1},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_TRANSITION"


def test_missing_document_returns_400_with_code(client):
    create = client.post("/api/obligations", json=make_payload(requires_document=True))
    obl_id = create.json()["id"]

    client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "in_progress", "version": 1},
    )

    response = client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "submitted", "version": 2},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "MISSING_DOCUMENT"


def test_submit_with_doc_succeeds(client):
    create = client.post("/api/obligations", json=make_payload(requires_document=True))
    obl_id = create.json()["id"]

    client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "in_progress", "version": 1},
    )

    upload = client.post(
        f"/api/obligations/{obl_id}/documents",
        files={"file": ("report.pdf", b"PDFDATA", "application/pdf")},
    )
    assert upload.status_code == 201
    doc_id = upload.json()["id"]

    response = client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "submitted", "version": 2, "document_id": doc_id},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "submitted"


def test_version_conflict_returns_409_with_code(client):
    create = client.post("/api/obligations", json=make_payload())
    obl_id = create.json()["id"]

    client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "in_progress", "version": 1},
    )

    response = client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "pending", "version": 1},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "VERSION_CONFLICT"


def test_validation_error_returns_422_with_code(client):
    response = client.post(
        "/api/obligations",
        json={"title": "Missing required fields"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "details" in data


def test_update_obligation_patches_fields(client):
    create = client.post("/api/obligations", json=make_payload(title="Old Title"))
    obl_id = create.json()["id"]

    response = client.patch(
        f"/api/obligations/{obl_id}",
        json={"title": "New Title", "description": "Updated desc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "Updated desc"
    assert data["version"] == 2


def test_history_endpoint_returns_list(client):
    create = client.post("/api/obligations", json=make_payload())
    obl_id = create.json()["id"]
    client.post(
        f"/api/obligations/{obl_id}/transitions",
        json={"to_status": "in_progress", "version": 1, "actor": "alice"},
    )

    response = client.get(f"/api/obligations/{obl_id}/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["actor"] == "alice"


def test_upload_document_returns_summary(client):
    create = client.post("/api/obligations", json=make_payload())
    obl_id = create.json()["id"]

    response = client.post(
        f"/api/obligations/{obl_id}/documents",
        files={"file": ("report.pdf", b"PDFCONTENT", "application/pdf")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "report.pdf"
    assert data["size"] == len(b"PDFCONTENT")
