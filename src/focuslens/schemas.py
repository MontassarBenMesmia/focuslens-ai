from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SessionLabel = Literal["stable", "variable", "interrupted"]
SignalSource = Literal["camera", "synthetic", "manual"]


class SignalInput(BaseModel):
    """Numeric observations only. Raw images and identity fields are forbidden."""

    model_config = ConfigDict(extra="forbid")

    eye_openness: float = Field(ge=0.0, le=1.0, examples=[0.72])
    gaze_stability: float = Field(ge=0.0, le=1.0, examples=[0.81])
    head_alignment: float = Field(ge=0.0, le=1.0, examples=[0.76])
    blink_rate: float = Field(ge=0.0, le=60.0, examples=[16.0])
    mouth_activity: float = Field(ge=0.0, le=1.0, examples=[0.18])
    face_presence: float = Field(ge=0.0, le=1.0, examples=[1.0])
    movement_level: float = Field(ge=0.0, le=1.0, examples=[0.24])
    framing_stability: float = Field(ge=0.0, le=1.0, examples=[0.79])
    source: SignalSource = Field(default="manual")
    observation_window_seconds: float = Field(default=10.0, ge=1.0, le=300.0)
    consent_confirmed: bool = Field(
        description="Confirms informed, voluntary authorization for this analysis."
    )
    adult_self_use_confirmed: bool = Field(
        description="Confirms the camera subject is an adult analyzing only themselves."
    )
    persist: bool = Field(
        default=False,
        description="Store numeric results locally. Raw media is never accepted or stored.",
    )

    @model_validator(mode="after")
    def require_consent(self) -> "SignalInput":
        if not self.consent_confirmed:
            raise ValueError("consent_confirmed must be true")
        if not self.adult_self_use_confirmed:
            raise ValueError("adult_self_use_confirmed must be true")
        return self

    def feature_values(self) -> list[float]:
        return [
            self.eye_openness,
            self.gaze_stability,
            self.head_alignment,
            self.blink_rate,
            self.mouth_activity,
            self.face_presence,
            self.movement_level,
            self.framing_stability,
        ]


class Factor(BaseModel):
    feature: str
    influence: Literal["supports", "reduces"]
    magnitude: float


class AnalysisResult(BaseModel):
    observation_id: str | None
    session_label: SessionLabel
    confidence: float
    stability_score: float
    signal_quality: float
    factors: list[Factor]
    model_version: str
    processed_at: datetime
    privacy: str = "numeric-signals-only"


class Summary(BaseModel):
    persisted_observations: int
    average_stability_score: float
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
