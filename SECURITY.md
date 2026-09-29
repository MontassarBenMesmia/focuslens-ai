# Security policy

## Supported version

Security updates target the latest commit on `main`.

## Reporting

Please report potential vulnerabilities privately through GitHub's security advisory feature. Do not open a public issue containing exploit details, credentials, personal data, or biometric material.

## Deployment warning

FocusLens is configured for local demonstration. Before any networked deployment, add authentication, TLS, rate limiting, strict origin controls, encrypted storage, retention limits, monitoring, and a formal privacy/legal review.

Never use the project to process data about children or other vulnerable groups.

Camera mode must continue to process frames locally. Treat any change that uploads, records, logs,
or persists raw media as a security- and privacy-sensitive design change requiring explicit review.
