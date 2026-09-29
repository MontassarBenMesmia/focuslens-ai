from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


AttentionLabel = Literal["focused", "neutral", "distracted"]
EnergySignal = Literal["steady", "elevated", "fatigue-signal"]


class SignalInput(BaseModel):
    """Numeric observations only. Raw images and identity fields are forbidden."""

    model_config = ConfigDict(extra="forbid")

    eye_openness: float = Field(ge=0.0, le=1.0, examples=[0.72])
    gaze_stability: float = Field(ge=0.0, le=1.0, examples=[0.81])
    head_alignment: float = Field(ge=0.0, le=1.0, examples=[0.76])
    blink_rate: float = Field(ge=0.0, le=60.0, examples=[16.0])
    mouth_activity: float = Field(ge=0.0, le=1.0, examples=[0.18])
    face_presence: float = Field(ge=0.0, le=1.0, examples=[1.0])
    hand_activity: float = Field(ge=0.0, le=1.0, examples=[0.24])
    posture_stability: float = Field(ge=0.0, le=1.0, examples=[0.79])
    consent_confirmed: bool = Field(
        description="Confirms that the signal source is authorized for this local analysis."
    )
    persist: bool = Field(
        default=False,
        description="Store numeric results locally. Raw media is never accepted or stored.",
    )

    @model_validator(mode="after")
    def require_consent(self) -> "SignalInput":
        if not self.consent_confirmed:
            raise ValueError("consent_confirmed must be true")
        return self

    def feature_values(self) -> list[float]:
        return [
            self.eye_openness,
            self.gaze_stability,
            self.head_alignment,
            self.blink_rate,
            self.mouth_activity,
            self.face_presence,
            self.hand_activity,
            self.posture_stability,
        ]


class Factor(BaseModel):
    feature: str
    influence: Literal["supports", "reduces"]
    magnitude: float


class AnalysisResult(BaseModel):
    observation_id: str | None
    attention_label: AttentionLabel
    confidence: float
    attention_score: float
    energy_signal: EnergySignal
    fatigue_signal: float
    factors: list[Factor]
    model_version: str
    processed_at: datetime
    privacy: str = "numeric-signals-only"


class Summary(BaseModel):
    persisted_observations: int
    average_attention_score: float
    label_counts: dict[str, int]
    latest_processed_at: datetime | None


class ModelCard(BaseModel):
    name: str
    version: str
    model_type: str
    training_source: str
    features: list[str]
    intended_use: str
    limitations: list[str]
    metrics: dict[str, float]
