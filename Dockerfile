FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY evaluators.py .
COPY test_cases.json .
COPY predictions.json .
COPY scripts/ scripts/
COPY .env.example .env

# Create directories for input/output
RUN mkdir -p /app/traces /app/results /app/langsmith_traces

# Copy existing traces
COPY langsmith_traces/ /app/langsmith_traces/

# Copy entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# Make scripts executable
RUN chmod +x scripts/*.py /app/docker-entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command runs the full evaluation pipeline
CMD ["python", "evaluators.py", "--tests", "test_cases.json", "--predictions", "predictions.json"]
