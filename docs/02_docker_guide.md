# Docker Fundamentals for ML Deployment

## 1. Introduction to Docker

### 1.1 What is Docker?

Docker is a platform for packaging applications and their dependencies into **containers**. Think of a container as a lightweight, standalone executable package that includes everything needed to run your application: code, runtime, system tools, libraries, and settings.

**The Problem Docker Solves:**
- "It works on my machine" syndrome
- Dependency conflicts between projects
- Complex deployment procedures
- Environment inconsistencies (dev vs production)

**Docker's Solution:**
Package everything your app needs into a container that runs the same way everywhere.

### 1.2 Virtual Machines vs Containers

**Virtual Machines (Old Way):**
```
┌─────────────────────────────────┐
│       Application               │
├─────────────────────────────────┤
│       Guest OS (Ubuntu)         │  ← Full OS = Heavy
├─────────────────────────────────┤
│       Hypervisor                │
├─────────────────────────────────┤
│       Host OS                   │
└─────────────────────────────────┘
```
- Full operating system for each app
- Gigabytes of disk space
- Slow startup (minutes)

**Containers (Docker Way):**
```
┌─────────────────────────────────┐
│       Application               │
├─────────────────────────────────┤
│       Container Runtime         │  ← Shares Host OS = Light
├─────────────────────────────────┤
│       Host OS                   │
└─────────────────────────────────┘
```
- Shares host OS kernel
- Megabytes of disk space
- Fast startup (seconds)

### 1.3 Core Docker Concepts

**Image**: A blueprint/template for a container
- Like a class in programming (definition)
- Read-only
- Built from instructions in a Dockerfile
- Example: `python:3.9` image contains Python 3.9 and basic tools

**Container**: A running instance of an image
- Like an object in programming (instance)
- Writable layer on top of the image
- Isolated process with its own filesystem
- Example: Your FastAPI app running inside a container

**Dockerfile**: A text file with instructions to build an image
- Defines the base image
- Installs dependencies
- Copies application code
- Specifies how to run the app

**Registry**: A storage location for Docker images
- Docker Hub: Public registry (like GitHub for images)
- Private registries: For company-internal images

## 2. Dockerfile Anatomy

### 2.1 Basic Structure

A Dockerfile is a series of instructions executed in order:

```dockerfile
# Base image - starting point
FROM python:3.9

# Set working directory inside container
WORKDIR /app

# Copy files from host to container
COPY requirements.txt .

# Run commands during build
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Command to run when container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### 2.2 Key Instructions Explained

**FROM**: Specifies the base image
```dockerfile
FROM python:3.9-slim
# slim = smaller image without unnecessary packages
```

**WORKDIR**: Sets the working directory
```dockerfile
WORKDIR /app
# All subsequent commands run from /app
# Creates directory if it doesn't exist
```

**COPY**: Copies files from host to container
```dockerfile
COPY source destination
COPY requirements.txt /app/
COPY . .  # Copy everything from current directory
```

**RUN**: Executes commands during image build
```dockerfile
RUN pip install torch
RUN apt-get update && apt-get install -y libgl1
# Each RUN creates a new layer in the image
```

**CMD**: Default command when container starts
```dockerfile
CMD ["python", "app.py"]
# Can be overridden when running container
```

**ENTRYPOINT**: Like CMD but cannot be overridden easily
```dockerfile
ENTRYPOINT ["uvicorn"]
CMD ["app.main:app"]
# Final command: uvicorn app.main:app
```

**ENV**: Sets environment variables
```dockerfile
ENV MODEL_NAME=yolov8n.pt
ENV PORT=8000
```

**EXPOSE**: Documents which port the app uses
```dockerfile
EXPOSE 8000
# Informational only - doesn't actually publish the port
```

**ARG**: Build-time variables
```dockerfile
ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}
```

## 3. Image Layers and Caching

### 3.1 How Layers Work

Each Dockerfile instruction creates a **layer**:

```dockerfile
FROM python:3.9          # Layer 1: Base image
COPY requirements.txt .  # Layer 2: Requirements file
RUN pip install -r ...   # Layer 3: Installed packages
COPY . .                 # Layer 4: Application code
```

**Why This Matters:**
- Docker caches each layer
- If a layer hasn't changed, Docker reuses it (fast!)
- If a layer changes, all subsequent layers rebuild

### 3.2 Optimization Strategy

**Bad Order (Slow):**
```dockerfile
COPY . .                    # Changes often → rebuilds everything below
RUN pip install -r requirements.txt
```
Every code change triggers dependency reinstallation!

**Good Order (Fast):**
```dockerfile
COPY requirements.txt .      # Changes rarely
RUN pip install -r requirements.txt
COPY . .                     # Changes often
```
Code changes don't trigger dependency reinstallation.

**Principle**: Put frequently changing instructions at the bottom.

## 4. Multi-Stage Builds

### 4.1 The Problem

ML models often require:
- Build tools (compilers, development headers)
- Large development dependencies
- These aren't needed at runtime

Result: Bloated images (2-3GB+)

### 4.2 Multi-Stage Solution

Build in stages, only keep what you need:

```dockerfile
# Stage 1: Builder (has everything)
FROM python:3.9 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime (minimal)
FROM python:3.9-slim
WORKDIR /app
# Copy only installed packages from builder
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "app.py"]
```

**Benefits:**
- Final image contains only runtime dependencies
- 50-70% size reduction
- Faster deployment

## 5. Docker for ML Applications

### 5.1 Special Considerations

**Large Dependencies:**
```dockerfile
# OpenCV needs system libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
```

**Model Files:**
Option 1: Bake into image (simple, larger image)
```dockerfile
COPY models/ /app/models/
```

Option 2: Download at startup (smaller image, slower startup)
```dockerfile
CMD python download_model.py && uvicorn app.main:app
```

Option 3: Mount as volume (best for development)
```bash
docker run -v ./models:/app/models myapp
```

**PyTorch/TensorFlow:**
- Use CPU-only versions for smaller images
- GPU support requires NVIDIA Docker runtime
```dockerfile
# CPU version (smaller)
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 5.2 Health Checks

Tell Docker how to verify your app is healthy:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

This runs every 30 seconds:
- Success: Container marked healthy
- 3 failures: Container marked unhealthy

## 6. Docker Compose

### 6.1 What is Docker Compose?

Docker Compose manages multi-container applications using a YAML file.

**Why Use It:**
- Define all services in one file
- Start everything with one command
- Manage networks and volumes easily
- Perfect for development and simple deployments

### 6.2 Basic Structure

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_NAME=yolov8n.pt
    volumes:
      - ./models:/app/models
```

### 6.3 Key Concepts

**Services**: Individual containers
```yaml
services:
  api:        # Your FastAPI app
  redis:      # Cache (if needed)
  postgres:   # Database (if needed)
```

**Ports**: Map host port to container port
```yaml
ports:
  - "8000:8000"  # host:container
  - "80:8000"    # Map container's 8000 to host's 80
```

**Volumes**: Persist data or share files
```yaml
volumes:
  - ./data:/app/data        # Bind mount (dev)
  - model_cache:/app/cache  # Named volume (prod)
```

**Environment Variables**:
```yaml
environment:
  - DEBUG=false
  - MODEL_NAME=yolov8n.pt
env_file:
  - .env  # Load from file
```

**Networks**: Connect containers
```yaml
networks:
  app_network:
    driver: bridge
```

## 7. Building and Running

### 7.1 Build an Image

```bash
# Basic build
docker build -t my-api .

# Build with specific Dockerfile
docker build -f Dockerfile.prod -t my-api:prod .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.9 -t my-api .

# No cache (clean build)
docker build --no-cache -t my-api .
```

**Flags:**
- `-t`: Tag (name) the image
- `-f`: Specify Dockerfile path
- `--build-arg`: Pass build-time variables
- `--no-cache`: Don't use cached layers

### 7.2 Run a Container

```bash
# Basic run
docker run my-api

# Run in background (detached)
docker run -d my-api

# Map ports
docker run -p 8000:8000 my-api

# Set environment variables
docker run -e MODEL_NAME=yolov8s.pt my-api

# Mount volumes
docker run -v $(pwd)/models:/app/models my-api

# Name the container
docker run --name my-api-container my-api

# Remove container after it stops
docker run --rm my-api

# Complete example
docker run -d \
  --name object-detection-api \
  -p 8000:8000 \
  -e MODEL_NAME=yolov8n.pt \
  -v $(pwd)/models:/app/models \
  --restart unless-stopped \
  my-api
```

**Flags:**
- `-d`: Detached (background)
- `-p`: Port mapping
- `-e`: Environment variable
- `-v`: Volume mount
- `--name`: Container name
- `--rm`: Auto-remove after stop
- `--restart`: Restart policy

### 7.3 Docker Compose Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild images before starting
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Restart a service
docker-compose restart api

# Execute command in running container
docker-compose exec api bash
```

## 8. Common Docker Commands

### 8.1 Image Management

```bash
# List images
docker images

# Remove image
docker rmi image-name

# Remove unused images
docker image prune

# Tag an image
docker tag my-api:latest my-api:v1.0

# Save image to file
docker save -o my-api.tar my-api

# Load image from file
docker load -i my-api.tar
```

### 8.2 Container Management

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop container
docker stop container-name

# Start stopped container
docker start container-name

# Remove container
docker rm container-name

# Remove all stopped containers
docker container prune

# View container logs
docker logs container-name

# Follow logs (real-time)
docker logs -f container-name

# Execute command in running container
docker exec -it container-name bash

# View container resource usage
docker stats

# Inspect container details
docker inspect container-name
```

### 8.3 System Management

```bash
# View Docker disk usage
docker system df

# Clean up everything unused
docker system prune -a

# View all volumes
docker volume ls

# Remove unused volumes
docker volume prune
```

## 9. Best Practices for ML Deployment

### 9.1 Image Size Optimization

**Use Slim Base Images:**
```dockerfile
# Good: 150MB base
FROM python:3.9-slim

# Avoid: 900MB base
FROM python:3.9
```

**Combine RUN Commands:**
```dockerfile
# Bad: Multiple layers
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2

# Good: One layer
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*
```

**Use .dockerignore:**
```
venv/
__pycache__/
*.pyc
.git/
tests/
docs/
*.md
```

**Install CPU-only Frameworks:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 9.2 Security Best Practices

**Don't Run as Root:**
```dockerfile
# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

**Use Specific Image Versions:**
```dockerfile
# Bad: Version changes unexpectedly
FROM python:3.9

# Good: Locked to specific version
FROM python:3.9.18-slim
```

**Scan for Vulnerabilities:**
```bash
docker scan my-api:latest
```

### 9.3 Production Considerations

**Use Production ASGI Server:**
```dockerfile
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

**Set Resource Limits:**
```bash
docker run --memory="2g" --cpus="2.0" my-api
```

**Implement Health Checks:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8000/health || exit 1
```

**Use Restart Policies:**
```bash
docker run --restart=unless-stopped my-api
```

## 10. Debugging Docker Containers

### 10.1 Common Issues

**Container Exits Immediately:**
```bash
# View logs
docker logs container-name

# Run interactively to see errors
docker run -it my-api /bin/bash
```

**Port Already in Use:**
```bash
# Find process using port
lsof -i :8000

# Use different host port
docker run -p 8001:8000 my-api
```

**Permission Denied:**
```bash
# Check file permissions
ls -la

# Fix ownership in Dockerfile
RUN chown -R appuser:appuser /app
```

**Out of Memory:**
```bash
# Check container stats
docker stats

# Increase memory limit
docker run --memory="4g" my-api
```

### 10.2 Debugging Techniques

**Interactive Shell:**
```bash
# Start container with bash
docker run -it my-api /bin/bash

# Access running container
docker exec -it container-name bash
```

**Override Entrypoint:**
```bash
# Skip CMD and drop into shell
docker run -it --entrypoint /bin/bash my-api
```

**Check Build Stages:**
```bash
# Build with progress output
docker build --progress=plain -t my-api .
```

**Inspect Image Layers:**
```bash
docker history my-api
```

## 11. Docker in Production

### 11.1 Deployment Platforms

**Cloud Container Services:**
- **AWS ECS/Fargate**: Managed container orchestration
- **Google Cloud Run**: Serverless containers
- **Azure Container Instances**: Simple container hosting
- **Railway/Render**: Developer-friendly platforms

**Container Orchestration:**
- **Kubernetes**: Industry standard for large-scale deployments
- **Docker Swarm**: Simpler alternative to Kubernetes
- **Nomad**: HashiCorp's orchestrator

### 11.2 CI/CD Integration

**Build on Push:**
```yaml
# GitHub Actions example
- name: Build Docker image
  run: docker build -t myapp:${{ github.sha }} .

- name: Push to registry
  run: docker push myapp:${{ github.sha }}
```

**Automated Testing:**
```bash
# Test in container
docker run myapp:test pytest
```

## 12. Summary

Docker enables consistent, reproducible deployments by:

1. **Packaging** - Bundle app + dependencies
2. **Isolation** - Each container is independent
3. **Portability** - Run anywhere Docker runs
4. **Efficiency** - Lightweight compared to VMs

**Key Takeaways:**
- Use multi-stage builds for smaller images
- Optimize layer caching for faster builds
- Follow security best practices (non-root user, specific versions)
- Use docker-compose for easier development
- Implement health checks for production

## Next Steps

Proceed to [Deployment Guide](03_deployment_guide.md) to learn about deploying your containerized application to cloud platforms.
