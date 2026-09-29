# Synthetic data card

## Motivation

The original academic archives referenced camera captures, an external facial-expression dataset, collected concentration metrics, and trained binary artifacts. None are included here because their consent, ownership, and demographic coverage cannot be established from the archives.

## Generation

`src/focuslens/synthetic.py` samples eight numeric variables from bounded statistical distributions using NumPy's deterministic random generator. Labels come from a documented noisy scoring function.

## Personal data

None. The generator creates no names, images, identity embeddings, contact information, location, demographics, or persistent identifiers.

## Appropriate use

The data is suitable for tests, demonstrations, API examples, and ML-pipeline exercises. It is not suitable for scientific claims, behavioral research, or deployment decisions.
