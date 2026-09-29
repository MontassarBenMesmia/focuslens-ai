from __future__ import annotations

from datetime import UTC, datetime

from .model import FocusModel
from .schemas import AnalysisResult, ModelCard, SignalInput, Summary
from .store import ObservationStore


class AnalysisService:
    def __init__(self, model: FocusModel, store: ObservationStore):
        self.model = model
        self.store = store

    def analyze(self, signal: SignalInput) -> AnalysisResult:
        prediction = self.model.predict(signal)
        processed_at = datetime.now(UTC)
        observation_id = None
        if signal.persist:
            observation_id = self.store.save(
                signal=signal,
                label=prediction.label,
                confidence=prediction.confidence,
                stability_score=prediction.score,
                signal_quality=prediction.signal_quality,
                processed_at=processed_at,
            )
        return AnalysisResult(
            observation_id=observation_id,
            session_label=prediction.label,
            confidence=prediction.confidence,
            stability_score=prediction.score,
            signal_quality=prediction.signal_quality,
            factors=prediction.factors,
            model_version=self.model.version,
            processed_at=processed_at,
        )

    def summary(self) -> Summary:
        return self.store.summary()

    def model_card(self) -> ModelCard:
        return ModelCard(
            name="FocusLens session-stability classifier",
            version=self.model.version,
            model_type="standardized multinomial logistic regression",
            training_source="deterministic synthetic observations generated in source code",
            features=self.model.features,
            intended_use=(
                "Adult, voluntary self-reflection on observable webcam-derived session signals; "
                "not evaluating people or making educational, employment, medical, or safety decisions."
            ),
            limitations=[
                "Synthetic training data does not represent real-world populations.",
                "The output describes short-window signal stability, not attention, emotion, intent, or health.",
                "Predictions must not be used to grade, discipline, rank, identify, or diagnose anyone.",
                "Performance metrics measure fit to synthetic labels only.",
            ],
            metrics=self.model.metrics,
        )
