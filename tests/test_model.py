from pathlib import Path

from focuslens.model import FocusModel, train_model
from focuslens.schemas import SignalInput


def test_model_trains_and_explains_prediction(tmp_path: Path) -> None:
    artifact = tmp_path / "model.joblib"
    metrics = train_model(artifact, samples=1_200)
    model = FocusModel(artifact)
    result = model.predict(
        SignalInput(
            eye_openness=0.82,
            gaze_stability=0.88,
            head_alignment=0.84,
            blink_rate=17,
            mouth_activity=0.12,
            face_presence=1,
            hand_activity=0.2,
            posture_stability=0.86,
            consent_confirmed=True,
        )
    )

    assert artifact.exists()
    assert metrics["accuracy"] > 0.6
    assert result.label in {"focused", "neutral", "distracted"}
    assert 0 <= result.score <= 1
    assert len(result.factors) == 3
