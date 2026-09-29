# Responsible AI and privacy

## Intended use

FocusLens is a software-engineering demonstration of privacy-aware ML architecture, reproducible training, API validation, and model documentation.

## Prohibited use

Do not use FocusLens to:

- identify or recognize people;
- monitor children, students, employees, patients, or other vulnerable groups;
- grade, discipline, rank, hire, dismiss, diagnose, or make safety decisions;
- claim that appearance reliably reveals attention, emotion, intent, or health;
- process data without informed authorization and an appropriate legal basis.

## Privacy controls

- No raw-image or video endpoint exists.
- No biometric templates or identity labels are created.
- Unknown request fields are rejected.
- Persistence is disabled by default.
- Only bounded numeric demo signals can be stored locally.
- All training records are synthetic and generated from reviewed source code.

## Known limitations

Observable facial and posture metrics are context-dependent and culturally variable. Synthetic labels cannot establish real-world validity or fairness. The reported accuracy measures agreement with synthetic rules, not human behavior. The output is therefore a demonstration signal, never ground truth about a person.
