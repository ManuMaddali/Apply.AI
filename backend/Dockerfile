# Apply.AI Secure Production Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="Apply.AI Team"
LABEL version="2.0.0"
LABEL description="Secure AI Resume Tailoring API"

# Security: Create non-root user
RUN groupadd -r applyai && useradd -r -g applyai applyai

# Security: Install security updates and required packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        curl \
        libmagic1 \
        libmagic-dev \
        gcc \
        g++ \
        --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Security: Create necessary directories and set permissions
RUN mkdir -p uploads outputs vector_stores logs && \
    chown -R applyai:applyai /app && \
    chmod -R 755 /app && \
    chmod -R 700 uploads outputs vector_stores logs

# Security: Remove unnecessary files
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true

# Security: Switch to non-root user
USER applyai

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Security: Expose only necessary port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Security: Use specific command instead of shell
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 