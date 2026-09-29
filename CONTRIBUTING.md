# Contributing

Thank you for improving FocusLens.

## Local workflow

1. Create a branch from `main`.
2. Install the development dependencies with `python -m pip install -e ".[dev]"`.
3. Run `python -m pytest` and `npm test`.
4. Keep pull requests focused and document behavior changes.

## Privacy requirements

Contributions must not include photographs, video, biometric embeddings, identity labels, personal datasets, child-related media, or serialized models trained on unverifiable data. Tests and examples must use generated numeric values.

Camera frames must remain inside the browser. Do not add raw-media endpoints, recording, frame uploads,
or weaken `extra="forbid"` request validation without a documented privacy review.
