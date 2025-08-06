# Dockerfile for Philosophical Multi-Agent Debate System
FROM python:3.12

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py ./

# Install the package in editable mode
RUN pip install -e .

# Add the app directory to PYTHONPATH to fix import issues
ENV PYTHONPATH=/app

# Default entrypoint
CMD ["python", "src/main.py"]
