from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from focuslens.api import app, get_service


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("FOCUSLENS_DATABASE_PATH", str(tmp_path / "focuslens.db"))
    monkeypatch.setenv("FOCUSLENS_MODEL_PATH", str(tmp_path / "model.joblib"))
    get_service.cache_clear()
    with TestClient(app) as test_client:
        yield test_client
    get_service.cache_clear()


def valid_payload() -> dict[str, float | bool]:
    return {
        "eye_openness": 0.72,
        "gaze_stability": 0.81,
        "head_alignment": 0.76,
        "blink_rate": 16,
        "mouth_activity": 0.18,
        "face_presence": 1,
        "hand_activity": 0.24,
        "posture_stability": 0.79,
        "consent_confirmed": True,
        "persist": False,
    }


def test_health_and_analysis(client: TestClient) -> None:
    health = client.get("/api/health")
    response = client.post("/api/v1/analyze", json=valid_payload())

    assert health.status_code == 200
    assert health.json()["privacy_mode"] == "numeric-signals-only"
    assert response.status_code == 200
    assert response.json()["observation_id"] is None
    assert response.json()["privacy"] == "numeric-signals-only"


def test_raw_image_field_is_rejected(client: TestClient) -> None:
    payload = valid_payload() | {"image": "data:image/jpeg;base64,not-accepted"}
    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == 422
    assert "image" in response.text


def test_consent_is_required(client: TestClient) -> None:
    payload = valid_payload() | {"consent_confirmed": False}
    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == 422


def test_persistence_is_explicit_and_numeric_only(client: TestClient) -> None:
    payload = valid_payload() | {"persist": True}
    response = client.post("/api/v1/analyze", json=payload)
    summary = client.get("/api/v1/summary")

    assert response.status_code == 200
    assert response.json()["observation_id"] is not None
    assert summary.json()["persisted_observations"] == 1


def test_model_card_discloses_limitations(client: TestClient) -> None:
    response = client.get("/api/v1/model-card")

    assert response.status_code == 200
    assert response.json()["training_source"].startswith("deterministic synthetic")
    assert len(response.json()["limitations"]) >= 3
