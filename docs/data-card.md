# Synthetic data card

## Motivation

FocusLens needs reproducible records for training, testing, and API demonstrations without collecting personal or biometric data. The repository therefore generates every training row from reviewed source code.

The historical academic archives referenced camera captures, collected concentration metrics, an external facial-expression dataset, and trained binary artifacts. None are included because their consent, ownership, and demographic coverage cannot be established.

## Generation

`src/focuslens/synthetic.py` samples eight bounded numeric variables with NumPy's seeded random generator. Labels (`stable`, `variable`, `interrupted`) come from a documented noisy scoring function that rewards stable geometry and penalizes movement.

These labels are definitions inside the demonstration, not ground truth collected from people.

## Personal data

None. The generator creates no names, images, videos, audio, identity embeddings, contact information, locations, demographics, or persistent identifiers.

## Camera data distinction

Live camera mode produces a short numeric observation at runtime. Those values are inference inputs, not training data, and are discarded after the response unless the user explicitly enables local numeric persistence. Frames are never sent to the API.

## Appropriate use

The synthetic data is suitable for tests, demonstrations, API examples, explainability exercises, and ML-pipeline development. It is not suitable for behavioral science, biometric research, population claims, model benchmarking, or deployment decisions.
