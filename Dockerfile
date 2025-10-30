# Multi-Stage Dockerfile for Object Detection API
# This uses a multi-stage build to create a smaller final image

# ==============================================================================
# Stage 1: Builder
# Purpose: Install all dependencies including build tools
# This stage has everything needed to compile Python packages
# ==============================================================================
FROM python:3.9-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies needed for building Python packages
# - build-essential: Compilers and build tools
# - libgl1: OpenCV dependency
# - libglib2.0-0: OpenCV dependency
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
# If requirements.txt doesn't change, this layer is cached
COPY requirements.txt .

# Install Python dependencies to /usr/local (accessible to all users)
# --no-cache-dir: Don't cache packages (saves space)
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Stage 2: Runtime
# Purpose: Create minimal image with only runtime dependencies
# This is the final image that will be deployed
# ==============================================================================
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install only runtime dependencies (no build tools)
# These are needed for OpenCV and other libraries to run
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
# Copy from /usr/local where pip installs by default (accessible to all users)
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create a non-root user for security BEFORE copying app code
# Running as root is a security risk in production
RUN useradd -m -u 1000 appuser

# Copy application code
# This is done AFTER installing dependencies for better caching
# (code changes more frequently than dependencies)
COPY --chown=appuser:appuser ./app /app/app

# Give appuser write permission to /app (needed for model downloads)
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000
# This is documentation - it doesn't actually publish the port
# You still need to use -p when running the container
EXPOSE 8000

# Health check
# Docker will periodically check if the container is healthy
# If this fails 3 times, the container is marked unhealthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
# Using CMD (not ENTRYPOINT) allows easy override for debugging
# --host 0.0.0.0: Listen on all network interfaces (required for Docker)
# --port 8000: Port to listen on
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
