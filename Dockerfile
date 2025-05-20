# ---- builder ----
FROM python:3.10-slim AS builder
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
