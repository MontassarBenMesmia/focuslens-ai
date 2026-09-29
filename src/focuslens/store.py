from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from uuid import uuid4

from .schemas import SignalInput, Summary


class ObservationStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS session_observations (
                    id TEXT PRIMARY KEY,
                    processed_at TEXT NOT NULL,
                    session_label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    stability_score REAL NOT NULL,
                    signal_quality REAL NOT NULL,
                    numeric_features TEXT NOT NULL
                )
                """
            )

    def save(
        self,
        signal: SignalInput,
        label: str,
        confidence: float,
        stability_score: float,
        signal_quality: float,
        processed_at: datetime,
    ) -> str:
        observation_id = str(uuid4())
        numeric_features = {
            name: value
            for name, value in signal.model_dump().items()
            if name not in {"consent_confirmed", "adult_self_use_confirmed", "persist"}
        }
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO session_observations (
                    id, processed_at, session_label, confidence,
                    stability_score, signal_quality, numeric_features
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation_id,
                    processed_at.astimezone(UTC).isoformat(),
                    label,
                    confidence,
                    stability_score,
                    signal_quality,
                    json.dumps(numeric_features, separators=(",", ":")),
                ),
            )
        return observation_id

    def summary(self) -> Summary:
        with self._connect() as connection:
            aggregate = connection.execute(
                """
                SELECT COUNT(*) AS total,
                       COALESCE(AVG(stability_score), 0) AS average_score,
                       MAX(processed_at) AS latest
                FROM session_observations
                """
            ).fetchone()
            label_rows = connection.execute(
                "SELECT session_label, COUNT(*) AS count FROM session_observations GROUP BY session_label"
            ).fetchall()
        return Summary(
            persisted_observations=int(aggregate["total"]),
            average_stability_score=round(float(aggregate["average_score"]), 4),
            label_counts={row["session_label"]: int(row["count"]) for row in label_rows},
            latest_processed_at=(datetime.fromisoformat(aggregate["latest"]) if aggregate["latest"] else None),
        )
