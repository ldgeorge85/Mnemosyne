FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Install Node.js for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Back to app directory
WORKDIR /app

# Expose port
EXPOSE 8001

# Start the FastAPI server
CMD ["python", "api/fastapi_server.py"]
