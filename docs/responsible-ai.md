# Responsible AI and privacy

## Intended use

FocusLens is a software-engineering demonstration of local computer vision, data minimization, validated APIs, reproducible synthetic ML, explanations, and privacy-aware delivery. Camera mode is limited to informed, voluntary adult self-use.

## What the result means

`stable`, `variable`, and `interrupted` describe how the eight measured numbers align with synthetic rules during a short window. They do not describe a person's attention, productivity, emotion, intent, character, ability, truthfulness, or health.

## Prohibited use

Do not use FocusLens to:

- analyze children or anyone other than the consenting adult operating it;
- monitor students, employees, patients, applicants, drivers, or vulnerable groups;
- identify or recognize people;
- grade, discipline, rank, hire, dismiss, diagnose, or make safety decisions;
- conduct covert or continuous surveillance;
- claim that appearance reliably reveals an internal state;
- process data without informed authorization and an appropriate legal basis.

## Privacy controls

- Camera permission is requested only after an explicit user action.
- Video is processed locally by MediaPipe and never sent to FastAPI.
- No screenshot, recording, audio, identity embedding, or demographic profile is created.
- The camera stops after 10 seconds, on manual stop, or when leaving the page.
- The API accepts bounded numeric fields only and rejects unexpected fields.
- Consent and adult self-use confirmation are mandatory.
- Persistence is disabled by default and limited to numeric records.
- Security headers restrict camera access and third-party connections.
- Training data is deterministic, synthetic, and generated from source code.

## Third-party runtime

Camera mode downloads pinned MediaPipe code/WASM from jsDelivr and a face-landmarker model from Google Storage. The application does not send frames to either host. Deployments with strict network or supply-chain requirements should self-host verified copies and update the Content Security Policy accordingly.

## Known limitations

Lighting, occlusion, eyewear, head position, camera placement, device performance, skin presentation, and MediaPipe behavior may change the numeric measurements. The 10-second window is too short for scientific or diagnostic conclusions. Synthetic labels cannot establish real-world validity or fairness. Model confidence reflects agreement with synthetic patterns only.

## Reporting concerns

Security and privacy concerns should follow the private reporting process in [SECURITY.md](../SECURITY.md). Do not attach real camera captures or personal data to public issues.
