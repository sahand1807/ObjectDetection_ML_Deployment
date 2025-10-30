# Real-Time Object Detection API

## Overview

This project implements a production-ready REST API for real-time object detection using FastAPI, containerized with Docker, and deployable to cloud platforms. The system accepts image uploads, processes them through a pre-trained deep learning model, and returns detected objects with bounding box coordinates.

## Project Architecture

```
┌─────────────┐      HTTP POST      ┌──────────────┐      ┌─────────────┐
│   Client    │ ──────────────────> │  FastAPI     │ ───> │   YOLOv5    │
│ (Web/Hugo)  │ <────────────────── │   Server     │ <─── │    Model    │
└─────────────┘      JSON Response  └──────────────┘      └─────────────┘
                                            │
                                            │
                                     ┌──────▼──────┐
                                     │   Docker    │
                                     │  Container  │
                                     └─────────────┘
```

## Technology Stack

- **FastAPI**: Modern, high-performance web framework for building APIs
- **PyTorch**: Deep learning framework for model inference
- **YOLOv5**: State-of-the-art object detection model
- **Docker**: Containerization platform for consistent deployment
- **Uvicorn**: Lightning-fast ASGI server

## Learning Objectives

By completing this project, you will understand:

1. **FastAPI Fundamentals**
   - RESTful API design principles
   - Asynchronous request handling
   - File upload processing
   - Request validation and error handling
   - API documentation with OpenAPI/Swagger

2. **Docker Containerization**
   - Multi-stage builds for optimization
   - Dependency management in containers
   - Port mapping and networking
   - Image size optimization techniques

3. **ML Model Deployment**
   - Loading pre-trained models in production
   - Inference optimization
   - Memory management
   - Response formatting

4. **Cloud Deployment**
   - CI/CD with GitHub integration
   - Environment configuration
   - Health checks and monitoring
   - CORS and security considerations

## Project Structure

```
ObjectDetection_ML_Deployment/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # Pydantic models for request/response
│   ├── inference.py            # Model loading and inference logic
│   └── config.py               # Configuration management
├── docs/
│   ├── 01_fastapi_fundamentals.md
│   ├── 02_docker_guide.md
│   ├── 03_deployment_guide.md
│   └── 04_hugo_integration.md
├── tests/
│   └── test_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Docker Desktop (optional for local development)
- Git

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload

# Access API documentation
open http://localhost:8000/docs
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t object-detection-api .

# Run the container
docker run -p 8000:8000 object-detection-api
```

## API Endpoints

### Health Check
```http
GET /health
```

Returns the operational status of the API.

### Object Detection
```http
POST /predict
Content-Type: multipart/form-data

file: <image-file>
confidence: <float> (optional, default: 0.5)
```

Returns JSON with detected objects, confidence scores, and bounding box coordinates.

## Development Timeline

- **Day 1**: FastAPI setup, model integration, local testing
- **Day 2**: Docker containerization, optimization, local deployment
- **Day 3**: Cloud deployment, Hugo integration, documentation

## Documentation

Comprehensive guides are available in the `docs/` directory:

1. [FastAPI Fundamentals](docs/01_fastapi_fundamentals.md) - Core concepts and implementation
2. [Docker Guide](docs/02_docker_guide.md) - Containerization best practices
3. [Deployment Guide](docs/03_deployment_guide.md) - Cloud deployment strategies
4. [Hugo Integration](docs/04_hugo_integration.md) - Client-side implementation

## Performance Considerations

- **Model Loading**: Model is loaded once at startup to minimize latency
- **Asynchronous Processing**: Non-blocking I/O for concurrent requests
- **Image Preprocessing**: Optimized OpenCV operations
- **Response Compression**: Automatic gzip compression for large payloads

## Security

- Input validation for file types and sizes
- Rate limiting to prevent abuse
- CORS configuration for cross-origin requests
- Environment-based configuration for sensitive data

## License

MIT License - See LICENSE file for details

## Contributing

This is an educational project. Feel free to fork and modify for your learning purposes.

## Acknowledgments

- YOLOv5 by Ultralytics
- FastAPI by Sebastián Ramírez
- PyTorch by Meta AI
