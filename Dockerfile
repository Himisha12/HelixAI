# ---------------------------------------------------
# Stage 1: Build & Dependencies
# ---------------------------------------------------
FROM python:3.10-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install uv package manager
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

COPY pyproject.toml .

# Install dependencies using uv into virtualenv
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install -e . pydantic-settings email-validator

# ---------------------------------------------------
# Stage 2: Final Production Environment
# ---------------------------------------------------
FROM python:3.10-slim as runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# Create non-root user for security best practice
RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -s /bin/bash -m appuser

COPY --from=builder /app/.venv /app/.venv
COPY app /app/app
COPY streamlit_app.py /app/
COPY .env.example /app/.env

USER appuser

EXPOSE 8000
EXPOSE 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
