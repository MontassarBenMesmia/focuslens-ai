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

from .schemas import Factor, SignalInput
from .synthetic import FEATURES, generate_training_data


MODEL_VERSION = "1.1.0"


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float
    score: float
    signal_quality: float
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
        stable_index = int(np.where(classifier.classes_ == "stable")[0][0])
        variable_index = int(np.where(classifier.classes_ == "variable")[0][0])
        score = float(probabilities[stable_index] + probabilities[variable_index] * 0.5)
        quality = float(
            np.clip(
                0.55 * signal.face_presence
                + 0.20 * signal.framing_stability
                + 0.15 * signal.head_alignment
                + 0.10 * signal.gaze_stability,
                0.0,
                1.0,
            )
        )

        return Prediction(
            label=label,
            confidence=round(confidence, 4),
            score=round(score, 4),
            signal_quality=round(quality, 4),
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
