# Docker Setup and Testing Guide

## Prerequisites

Before you can build and run the Docker container, you need Docker installed.

### Installing Docker

**macOS:**
1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

**Windows:**
1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop
3. Verify in PowerShell:
   ```powershell
   docker --version
   ```

## Building and Running

### Option 1: Using docker-compose (Recommended)

Docker Compose makes it easy to build and run with one command:

```bash
# Build and start in one command
docker-compose up --build

# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**What this does:**
- Builds the Docker image from the Dockerfile
- Creates a container named "object-detection-api"
- Maps port 8000 to your host
- Starts the API
- Sets up health checks

### Option 2: Using Docker commands directly

```bash
# 1. Build the image
docker build -t object-detection-api .

# 2. Run the container
docker run -d \
  --name object-detection-api \
  -p 8000:8000 \
  object-detection-api

# 3. Check if it's running
docker ps

# 4. View logs
docker logs -f object-detection-api

# 5. Stop the container
docker stop object-detection-api

# 6. Remove the container
docker rm object-detection-api
```

### Option 3: Using the test script

We've created a test script that automates everything:

```bash
./docker-test.sh
```

This script will:
1. Build the image
2. Start the container
3. Test the health endpoint
4. Test object detection
5. Show logs and stats

## Testing the API

Once the container is running, test it:

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Interactive Documentation
Open in browser: http://localhost:8000/docs

### 3. Object Detection
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@test_image.jpg"
```

## Understanding What Happens

### Build Process

When you run `docker build`:

1. **Stage 1 (Builder)**:
   - Starts with Python 3.9 slim image
   - Installs build dependencies (gcc, etc.)
   - Installs all Python packages from requirements.txt
   - This takes 5-10 minutes on first build

2. **Stage 2 (Runtime)**:
   - Fresh Python 3.9 slim image
   - Copies only the installed packages (not build tools)
   - Copies your application code
   - Creates non-root user
   - Sets up health check
   - Final image is ~800MB vs ~2GB without multi-stage

### First Run

On the first run, the container will:
1. Start the FastAPI application
2. Download the YOLO model (~6MB) from GitHub
3. Load the model into memory
4. Start accepting requests

**Expect 30-40 seconds** for the first startup (model download).

Subsequent starts are faster (~5 seconds) because the model is cached.

## Viewing Container Information

### List running containers
```bash
docker ps
```

### View logs
```bash
# All logs
docker logs object-detection-api

# Follow logs (real-time)
docker logs -f object-detection-api

# Last 50 lines
docker logs --tail 50 object-detection-api
```

### Resource usage
```bash
docker stats object-detection-api
```

### Inspect container
```bash
docker inspect object-detection-api
```

### Execute commands inside container
```bash
# Open a shell
docker exec -it object-detection-api /bin/bash

# Run a specific command
docker exec object-detection-api ls -la /app
```

## Troubleshooting

### Container exits immediately
```bash
# Check logs for errors
docker logs object-detection-api

# Run interactively to see errors
docker run -it object-detection-api /bin/bash
```

### Port already in use
```bash
# Use a different port
docker run -p 8001:8000 object-detection-api

# Find what's using the port
lsof -i :8000
```

### Image is too large
```bash
# Check image size
docker images object-detection-api

# View layer sizes
docker history object-detection-api
```

### Container is slow
```bash
# Check resource usage
docker stats object-detection-api

# Allocate more resources
docker run --memory="2g" --cpus="2.0" object-detection-api
```

### Model not loading
Check logs:
```bash
docker logs object-detection-api | grep -i "model\|error"
```

Common issues:
- Network issues (can't download model)
- Insufficient memory
- Permissions issues

## Image Optimization

Current image is optimized with:
- Multi-stage build (smaller final image)
- Python slim base image
- Minimal system dependencies
- No caching of pip packages
- Cleanup of apt lists

**Expected final size**: ~800MB
- Python: ~150MB
- PyTorch CPU: ~400MB
- Other dependencies: ~250MB

To reduce further:
- Use PyTorch CPU-only build
- Use Alpine Linux (more complex)
- Remove unnecessary dependencies

## Production Deployment

For production, consider:

1. **Resource limits**:
   ```bash
   docker run --memory="2g" --cpus="2.0" object-detection-api
   ```

2. **Restart policy**:
   ```bash
   docker run --restart=unless-stopped object-detection-api
   ```

3. **Environment variables**:
   ```bash
   docker run -e MODEL_NAME=yolov8s.pt object-detection-api
   ```

4. **Volume for model persistence**:
   ```bash
   docker run -v ./models:/app/models object-detection-api
   ```

5. **Health checks**: Already built into the image!

## Next Steps

Once you've verified the Docker container works:
1. Push to Docker Hub or GitHub Container Registry
2. Deploy to cloud platform (Railway, Render, AWS, etc.)
3. Set up CI/CD for automatic builds

See [Deployment Guide](docs/03_deployment_guide.md) for cloud deployment instructions.
