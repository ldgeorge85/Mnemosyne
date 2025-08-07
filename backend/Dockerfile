# Backend Dockerfile with multi-stage build
# Stage 1: Development
FROM python:3.11-slim AS development

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Create virtual environment
RUN python -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

# Install Python dependencies (includes CrewAI and Cognee for Phase 3)
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Development only needs the requirements installed
# The actual code will be mounted as a volume

# Stage 2: Production
FROM python:3.11-slim AS production

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from development stage
COPY --from=development /app/.venv /app/.venv

# Copy application code
COPY . .

# Expose API port
EXPOSE 8000

# Make startup script executable
RUN chmod +x /app/startup.sh

# Run the application
CMD ["/app/startup.sh"]
