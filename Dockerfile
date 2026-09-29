FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/MontassarBenMesmia/focuslens-ai" \
      org.opencontainers.image.description="Privacy-first on-device webcam signal analytics" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FOCUSLENS_ENV=production \
    FOCUSLENS_DATABASE_PATH=/app/data/focuslens.db \
    FOCUSLENS_MODEL_PATH=/app/artifacts/focus_model.joblib

RUN useradd --create-home --shell /usr/sbin/nologin focuslens
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . && mkdir -p data artifacts && chown -R focuslens:focuslens /app

USER focuslens
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://localhost:' + os.getenv('PORT', '8000') + '/api/health', timeout=2)"

CMD ["sh", "-c", "uvicorn focuslens.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
