# Model card

## Model details

- **Name:** FocusLens session-stability classifier
- **Version:** 1.1.0
- **Type:** standardized multinomial logistic regression
- **Framework:** scikit-learn
- **Artifact policy:** generated locally; never committed

## Intended use

FocusLens demonstrates an end-to-end, privacy-aware computer-vision and ML architecture for voluntary adult self-reflection. It classifies a short numeric observation window according to patterns defined by the synthetic generator.

It is not intended to measure attention, productivity, emotion, intent, fatigue, truthfulness, ability, or health.

## Inputs

Eight bounded numeric features: eye openness, gaze stability, head alignment, blink rate, mouth activity, face presence, movement level, and framing stability. Inputs may come from the local browser camera pipeline, manual sliders, or the synthetic-sample generator.

## Outputs

- synthetic session label: `stable`, `variable`, or `interrupted`;
- normalized stability score and class confidence;
- signal-quality estimate based on observable input quality;
- three leading signed feature contributions.

## Training and evaluation

The repository generates deterministic synthetic observations with a fixed random seed. Accuracy and macro F1 are calculated on a stratified synthetic holdout set and embedded in the generated artifact.

These metrics measure implementation consistency with synthetic labeling rules only. They are not evidence of real-world validity, fairness, or human-state inference.

## Limitations

- Webcam measurements vary with lighting, pose, eyewear, occlusion, camera quality, frame rate, and device performance.
- Iris and blendshape stability are observable geometry, not proof of attention or intent.
- Blink-rate extrapolation from a 10-second window is especially noisy.
- The synthetic model has not been validated on people or populations.
- A high confidence value means confidence relative to synthetic classes, not confidence about a person.

## Prohibited use

Do not use this model for surveillance, children, students, employees, patients, grading, discipline, hiring, diagnosis, safety, identity recognition, or any consequential decision. See [responsible-ai.md](responsible-ai.md).
