# ---- Builder stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv from official image (faster than pip install uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies into /app/.venv
RUN uv sync --frozen --no-dev --no-install-project

# ---- Runtime stage ----
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY docker/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

# Switch to non-root user
USER appuser

# Activate venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
