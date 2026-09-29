# Model card

## Model details

- **Name:** FocusLens engagement classifier
- **Version:** 1.0.0
- **Type:** standardized multinomial logistic regression
- **Framework:** scikit-learn
- **Artifact policy:** generated locally; never committed

## Inputs

Eight bounded numeric features: eye openness, gaze stability, head alignment, blink rate, mouth activity, face presence, hand activity, and posture stability.

## Outputs

- demonstration label: `focused`, `neutral`, or `distracted`;
- normalized attention score and confidence;
- non-diagnostic energy and fatigue signals;
- three leading signed feature contributions.

## Training data

The repository generates deterministic synthetic observations with a fixed random seed. It contains no photographs, videos, biometric identifiers, or personal records.

## Evaluation

Accuracy and macro F1 are calculated on a stratified synthetic holdout set and embedded in the generated artifact. These metrics measure implementation consistency only and must not be interpreted as evidence of real-world human-state inference.

## Ethical limitations

The model must not be used for consequential decisions, covert surveillance, identity recognition, or monitoring children. See [responsible-ai.md](responsible-ai.md).
