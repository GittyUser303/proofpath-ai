from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_returns_service_metadata() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ProofPath AI"


def test_dashboard_is_served_from_root() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "ProofPath" in response.text
    assert "Evidence Desk" in response.text


def test_streaming_investigation_returns_progress_events() -> None:
    client = TestClient(create_app())

    with client.stream(
        "POST",
        "/api/investigate/stream",
        json={"user_id": "test_user", "input": "Cold water after meals causes cancer.", "mode": "standard"},
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert '"event": "activity"' in body
    assert '"event": "complete"' in body
