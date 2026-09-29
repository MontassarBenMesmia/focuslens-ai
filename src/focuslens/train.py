from __future__ import annotations

import argparse
from pathlib import Path

from .model import train_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the deterministic FocusLens demo model")
    parser.add_argument("--output", type=Path, default=Path("artifacts/focus_model.joblib"))
    parser.add_argument("--samples", type=int, default=8_000)
    args = parser.parse_args()
    metrics = train_model(args.output, samples=args.samples)
    print(f"Model written to {args.output}")
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    main()
