# ---- builder ----
FROM python:3.10-slim AS builder
=======
# Dockerfile for Legion Web Interface

# Use an official Python runtime as a parent image
FROM ghcr.io/${GITHUB_REPOSITORY_OWNER}/legion-base:py310 as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt requirements.dev.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.dev.txt

# ---- runtime ----
FROM python:3.10-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY --from=builder /wheels /wheels
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir /wheels/*
COPY . .
CMD ["uvicorn", "legion.api:app", "--host", "0.0.0.0", "--port", "7803"]
