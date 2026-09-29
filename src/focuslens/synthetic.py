from __future__ import annotations

import numpy as np


FEATURES = [
    "eye_openness",
    "gaze_stability",
    "head_alignment",
    "blink_rate",
    "mouth_activity",
    "face_presence",
    "movement_level",
    "framing_stability",
]

LABELS = np.array(["interrupted", "variable", "stable"])


def generate_training_data(samples: int = 8_000, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Create deterministic, non-personal demo observations."""

    rng = np.random.default_rng(seed)
    eye_openness = rng.beta(4.2, 2.0, samples)
    gaze_stability = rng.beta(3.8, 2.1, samples)
    head_alignment = rng.beta(4.0, 1.9, samples)
    blink_rate = rng.normal(17.0, 7.0, samples).clip(0, 60)
    mouth_activity = rng.beta(2.0, 5.0, samples)
    face_presence = rng.binomial(1, 0.94, samples).astype(float)
    movement_level = rng.beta(2.3, 4.2, samples)
    framing_stability = rng.beta(3.7, 2.0, samples)

    matrix = np.column_stack(
        [
            eye_openness,
            gaze_stability,
            head_alignment,
            blink_rate,
            mouth_activity,
            face_presence,
            movement_level,
            framing_stability,
        ]
    )
    blink_balance = 1.0 - np.clip(np.abs(blink_rate - 17.0) / 30.0, 0.0, 1.0)
    latent_score = (
        0.14 * eye_openness
        + 0.24 * gaze_stability
        + 0.19 * head_alignment
        + 0.08 * blink_balance
        - 0.08 * mouth_activity
        + 0.15 * face_presence
        - 0.10 * movement_level
        + 0.19 * framing_stability
        + rng.normal(0.0, 0.075, samples)
    )
    encoded = np.where(latent_score < 0.48, 0, np.where(latent_score < 0.68, 1, 2))
    return matrix, LABELS[encoded]
