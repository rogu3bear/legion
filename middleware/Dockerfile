# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE ${SERVICE_PORT}
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "${SERVICE_PORT}"]
