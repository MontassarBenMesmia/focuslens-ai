from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    environment: str
    database_path: Path
    model_path: Path
    allowed_origins: tuple[str, ...]

    @classmethod
    def from_environment(cls) -> "Settings":
        origins = os.getenv("FOCUSLENS_ALLOWED_ORIGINS", "http://localhost:8000")
        return cls(
            environment=os.getenv("FOCUSLENS_ENV", "development"),
            database_path=Path(os.getenv("FOCUSLENS_DATABASE_PATH", "data/focuslens.db")),
            model_path=Path(os.getenv("FOCUSLENS_MODEL_PATH", "artifacts/focus_model.joblib")),
            allowed_origins=tuple(item.strip() for item in origins.split(",") if item.strip()),
        )
