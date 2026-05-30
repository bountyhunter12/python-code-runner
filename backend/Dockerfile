# Backend Dockerfile
FROM python:3.11-slim

# Install Docker CLI to communicate with host's Docker daemon via socket
# The socket is mounted at /var/run/docker.sock in docker-compose.yml
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker.io \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r docker || true \
    && usermod -aG docker root

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]