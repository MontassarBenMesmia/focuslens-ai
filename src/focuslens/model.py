from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .schemas import EnergySignal, Factor, SignalInput
from .synthetic import FEATURES, generate_training_data


MODEL_VERSION = "1.0.0"


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float
    score: float
    energy_signal: EnergySignal
    fatigue_signal: float
    factors: list[Factor]


def train_model(output_path: Path, samples: int = 8_000) -> dict[str, float]:
    features, labels = generate_training_data(samples=samples)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(max_iter=1_500, class_weight="balanced", random_state=42),
            ),
        ]
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "macro_f1": round(float(f1_score(y_test, predictions, average="macro")), 4),
        "samples": float(samples),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "features": FEATURES,
            "metrics": metrics,
            "version": MODEL_VERSION,
        },
        output_path,
    )
    return metrics


class FocusModel:
    def __init__(self, artifact_path: Path):
        if not artifact_path.exists():
            train_model(artifact_path)
        artifact = joblib.load(artifact_path)
        self.pipeline: Pipeline = artifact["pipeline"]
        self.features: list[str] = artifact["features"]
        self.metrics: dict[str, float] = artifact["metrics"]
        self.version: str = artifact["version"]

    def predict(self, signal: SignalInput) -> Prediction:
        row = np.asarray([signal.feature_values()], dtype=float)
        probabilities = self.pipeline.predict_proba(row)[0]
        classifier = self.pipeline.named_steps["classifier"]
        label_index = int(np.argmax(probabilities))
        label = str(classifier.classes_[label_index])
        confidence = float(probabilities[label_index])
        focused_index = int(np.where(classifier.classes_ == "focused")[0][0])
        neutral_index = int(np.where(classifier.classes_ == "neutral")[0][0])
        score = float(probabilities[focused_index] + probabilities[neutral_index] * 0.5)

        fatigue = self._fatigue_signal(signal)
        if fatigue >= 0.64:
            energy: EnergySignal = "fatigue-signal"
        elif signal.mouth_activity > 0.68 or signal.hand_activity > 0.76:
            energy = "elevated"
        else:
            energy = "steady"

        return Prediction(
            label=label,
            confidence=round(confidence, 4),
            score=round(score, 4),
            energy_signal=energy,
            fatigue_signal=round(fatigue, 4),
            factors=self._explain(row, label_index),
        )

    def _explain(self, row: np.ndarray, label_index: int) -> list[Factor]:
        scaler: StandardScaler = self.pipeline.named_steps["scaler"]
        classifier: LogisticRegression = self.pipeline.named_steps["classifier"]
        standardized = scaler.transform(row)[0]
        contributions = standardized * classifier.coef_[label_index]
        ranked = np.argsort(np.abs(contributions))[::-1][:3]
        return [
            Factor(
                feature=self.features[index],
                influence="supports" if contributions[index] >= 0 else "reduces",
                magnitude=round(float(abs(contributions[index])), 4),
            )
            for index in ranked
        ]

    @staticmethod
    def _fatigue_signal(signal: SignalInput) -> float:
        blink_deviation = min(abs(signal.blink_rate - 17.0) / 35.0, 1.0)
        value = (
            0.38 * (1.0 - signal.eye_openness)
            + 0.24 * blink_deviation
            + 0.20 * signal.mouth_activity
            + 0.18 * (1.0 - signal.posture_stability)
        )
        return float(np.clip(value, 0.0, 1.0))
