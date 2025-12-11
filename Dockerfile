
# -------- Base image: stable Python 3.11 on Debian slim --------
FROM python:3.15.0a1-slim AS base

# Prevent .pyc files & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (only what's typically needed)
# If you need Postgres (psycopg2) later, add: libpq-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------- Dependencies layer --------
# Copy only requirements first to leverage Docker caching
COPY requirements.txt /app/requirements.txt

# Pin wheel to reduce build variability; install reqs without cache
RUN pip install --upgrade --no-cache-dir pip wheel \
    && pip install --no-cache-dir -r requirements.txt

# -------- App layer --------
# Copy the rest of the project
COPY . /app

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the app port
EXPOSE 8000

# Optional: Healthcheck (basic TCP check)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import socket,sys; s=socket.socket(); s.settimeout(3); s.connect(('127.0.0.1',8000)); s.close(); sys.exit(0)" || exit 1

# -------- Runtime command --------
# Use Gunicorn (production-grade) with 2 workers; adjust module to your project's WSGI
# Replace 'calapp.wsgi:application' if your project name differs
#CMD ["gunicorn", "calapp.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2"]
CMD ["gunicorn", "soapmini.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2"] 