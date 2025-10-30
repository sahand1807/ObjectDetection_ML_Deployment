#!/bin/bash
# Docker Testing Script
# This script builds and tests the Docker container

set -e  # Exit on error

echo "===================================================="
echo "Docker Build & Test Script"
echo "===================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Build the image
echo -e "\n${BLUE}Step 1: Building Docker image...${NC}"
docker build -t object-detection-api:latest .

# Step 2: Check image size
echo -e "\n${GREEN}✓ Build complete!${NC}"
echo -e "\n${BLUE}Image details:${NC}"
docker images object-detection-api:latest

# Step 3: Start container
echo -e "\n${BLUE}Step 2: Starting container...${NC}"
docker run -d \
  --name test-api \
  -p 8000:8000 \
  object-detection-api:latest

# Step 4: Wait for startup
echo -e "\n${BLUE}Waiting for API to start...${NC}"
sleep 10

# Step 5: Test health endpoint
echo -e "\n${BLUE}Step 3: Testing health endpoint...${NC}"
curl -s http://localhost:8000/health | python3 -m json.tool

# Step 6: Test with sample image
echo -e "\n${BLUE}Step 4: Testing object detection...${NC}"
if [ -f "test_image.jpg" ]; then
    curl -s -X POST "http://localhost:8000/predict" \
      -F "file=@test_image.jpg" | python3 -m json.tool
else
    echo "test_image.jpg not found, skipping detection test"
fi

# Step 7: Check container logs
echo -e "\n${BLUE}Step 5: Container logs:${NC}"
docker logs test-api --tail 20

# Step 8: Check container stats
echo -e "\n${BLUE}Step 6: Container resource usage:${NC}"
docker stats test-api --no-stream

echo -e "\n${GREEN}✓ All tests passed!${NC}"
echo -e "\n${BLUE}Container is running at http://localhost:8000${NC}"
echo -e "View docs at: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "\nTo stop container: ${BLUE}docker stop test-api${NC}"
echo -e "To remove container: ${BLUE}docker rm test-api${NC}"
echo -e "To view logs: ${BLUE}docker logs -f test-api${NC}"
