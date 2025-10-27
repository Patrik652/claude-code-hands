# Claude Vision & Hands - Production Dockerfile
# Multi-stage build for optimal image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    CLAUDE_VISION_HOME="/app" \
    DATA_DIR="/data"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create app user (security best practice)
RUN groupadd -r claude && \
    useradd -r -g claude -d /app -s /sbin/nologin claude && \
    mkdir -p /app /data && \
    chown -R claude:claude /app /data

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=claude:claude . .

# Create necessary directories
RUN mkdir -p \
    /data/recordings \
    /data/memory \
    /data/logs \
    /data/screenshots \
    && chown -R claude:claude /data

# Switch to non-root user
USER claude

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.path.insert(0, '/app'); from integration.orchestrator import AIOrchestrator; print('OK')" || exit 1

# Expose ports
EXPOSE 8080 8081

# Default command (can be overridden)
CMD ["python3", "-m", "integration.server"]
