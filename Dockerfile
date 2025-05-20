# Dockerfile for Legion Web Interface

# Use an official Python runtime as a parent image
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies if needed (e.g., for specific DB drivers)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# --- Using requirements.txt ---
COPY requirements.txt .
# Install Python dependencies
# Use wheels for faster installation and smaller final image
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# --- Application Stage ---
FROM python:3.10-slim

WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy project code
# Make sure these paths correctly reflect your project structure relative to the Dockerfile
COPY ./interface /app/interface
COPY ./legion /app/legion
COPY ./memory /app/memory
COPY ./skills /app/skills

# Copy alembic config and versions
COPY alembic.ini /app/
COPY .env.example /app/.env.example

# Make scripts executable (if any are included and used)
# RUN chmod +x /app/scripts/*.sh

# Expose port
EXPOSE 27000

# Set the entrypoint command
# Run migrations first, then start the server
# Consider using a proper entrypoint script for more complex startup logic
# Command to run the application
CMD ["uvicorn", "interface.main:app", "--host", "0.0.0.0", "--port", "27000", "--log-level", "info"]
