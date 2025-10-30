# FastAPI Fundamentals for ML Deployment

## 1. Introduction to FastAPI

### 1.1 What is FastAPI?

FastAPI is a modern, high-performance web framework for building APIs with Python 3.9+ based on standard Python type hints. It was created by Sebastián Ramírez and has gained significant adoption in the machine learning deployment community due to its performance characteristics and developer experience.

### 1.2 Core Design Principles

**Type Safety**: FastAPI leverages Python's type hints to provide automatic request validation, serialization, and documentation generation. This reduces runtime errors and improves code maintainability.

**Asynchronous First**: Built on Starlette for web routing and Pydantic for data validation, FastAPI supports both synchronous and asynchronous request handlers, enabling high-concurrency applications.

**Standards-Based**: Implements OpenAPI (formerly Swagger) and JSON Schema standards, providing automatic interactive API documentation.

### 1.3 Why FastAPI for ML Deployment?

1. **Performance**: Comparable to NodeJS and Go in benchmarks due to ASGI support
2. **Automatic Validation**: Type hints ensure input data matches expected formats
3. **Interactive Documentation**: Auto-generated Swagger UI for testing endpoints
4. **Dependency Injection**: Clean architecture for model loading and configuration
5. **Production-Ready**: Built-in support for testing, CORS, middleware, and background tasks

## 2. Request-Response Cycle

### 2.1 HTTP Fundamentals

HTTP (Hypertext Transfer Protocol) operates on a request-response model:

```
Client → HTTP Request → Server
Client ← HTTP Response ← Server
```

**Request Components**:
- Method (GET, POST, PUT, DELETE)
- URL path (/predict, /health)
- Headers (Content-Type, Authorization)
- Body (JSON, form data, files)

**Response Components**:
- Status code (200 OK, 404 Not Found, 500 Error)
- Headers (Content-Type, Content-Length)
- Body (JSON response, file)

### 2.2 RESTful API Design

REST (Representational State Transfer) principles guide our API design:

- **Resource-Oriented**: URLs represent resources (/predictions, not /getPrediction)
- **HTTP Methods**: Use appropriate verbs (GET for retrieval, POST for creation)
- **Stateless**: Each request contains all necessary information
- **Status Codes**: Use standard HTTP codes to indicate outcomes

## 3. FastAPI Application Structure

### 3.1 Application Instance

The core of FastAPI is the application instance:

```python
from fastapi import FastAPI

app = FastAPI(
    title="Object Detection API",
    description="Real-time object detection using YOLOv5",
    version="1.0.0"
)
```

This creates an ASGI application that handles routing, middleware, and lifecycle events.

### 3.2 Route Decorators

Routes map URL patterns to Python functions:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

The decorator `@app.get()` registers this function to handle GET requests to `/health`.

### 3.3 Path Operations

FastAPI supports all HTTP methods:
- `@app.get()` - Retrieve resources
- `@app.post()` - Create resources or trigger actions
- `@app.put()` - Update resources
- `@app.delete()` - Remove resources

## 4. Request Handling

### 4.1 File Uploads

For ML applications, handling file uploads is critical:

```python
from fastapi import UploadFile, File

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    # Process image
    return {"filename": file.filename}
```

**Key Concepts**:
- `UploadFile`: FastAPI's file upload type with async methods
- `File(...)`: Dependency marker indicating required file
- `await file.read()`: Asynchronous file reading (non-blocking)

### 4.2 Query Parameters

Query parameters pass optional configuration:

```python
@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    confidence: float = 0.5,
    iou_threshold: float = 0.45
):
    # Use parameters in inference
    pass
```

Access via: `/predict?confidence=0.7&iou_threshold=0.5`

### 4.3 Request Validation

Pydantic models define expected data structures:

```python
from pydantic import BaseModel, Field

class PredictionConfig(BaseModel):
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0)
    max_detections: int = Field(100, ge=1, le=1000)
```

FastAPI automatically validates requests against these schemas.

## 5. Response Models

### 5.1 Structured Responses

Define clear response formats:

```python
from typing import List

class BoundingBox(BaseModel):
    x_min: int
    y_min: int
    x_max: int
    y_max: int

class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: BoundingBox

class PredictionResponse(BaseModel):
    detections: List[Detection]
    inference_time_ms: float
    image_size: tuple[int, int]
```

### 5.2 Response Status Codes

Indicate operation outcomes:

```python
from fastapi import status

@app.post("/predict", status_code=status.HTTP_200_OK)
async def predict(file: UploadFile = File(...)):
    # Process
    return response
```

Common codes:
- 200: Success
- 400: Bad Request (invalid input)
- 500: Internal Server Error

## 6. Error Handling

### 6.1 HTTPException

Raise exceptions for error cases:

```python
from fastapi import HTTPException

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
```

### 6.2 Custom Exception Handlers

Handle specific errors globally:

```python
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )
```

## 7. Dependency Injection

### 7.1 Concept

Dependencies are reusable components that can be injected into routes:

```python
from fastapi import Depends

def get_model():
    # Load model once
    return model

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model = Depends(get_model)
):
    # Use model for inference
    pass
```

### 7.2 Startup Events

Initialize resources when the application starts:

```python
@app.on_event("startup")
async def load_model():
    app.state.model = torch.load("model.pt")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    model = app.state.model
    # Perform inference
```

This ensures the model loads once, not on every request.

## 8. Middleware and CORS

### 8.1 Middleware Concept

Middleware processes requests before they reach route handlers:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8.2 CORS Explained

Cross-Origin Resource Sharing (CORS) allows web applications on different domains to access your API. Essential for Hugo site integration.

## 9. Automatic Documentation

### 9.1 Interactive API Docs

FastAPI automatically generates:
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`

These provide:
- Endpoint descriptions
- Request/response schemas
- Interactive testing interface

### 9.2 Enhancing Documentation

Add descriptions to routes:

```python
@app.post(
    "/predict",
    summary="Detect objects in image",
    description="Accepts an image and returns detected objects with bounding boxes",
    response_description="List of detected objects"
)
async def predict(file: UploadFile = File(description="Image file (JPG, PNG)")):
    pass
```

## 10. Asynchronous Programming

### 10.1 Sync vs Async

**Synchronous** (blocking):
```python
def read_file():
    data = file.read()  # Waits here, blocks thread
    return data
```

**Asynchronous** (non-blocking):
```python
async def read_file():
    data = await file.read()  # Releases thread while waiting
    return data
```

### 10.2 When to Use Async

Use `async def` when:
- Performing I/O operations (file reads, network requests)
- Handling multiple concurrent requests
- Interfacing with async libraries

Use regular `def` when:
- Performing CPU-bound operations (model inference)
- Using synchronous libraries

### 10.3 Best Practice for ML Inference

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()  # Async I/O

    # CPU-bound inference in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        model.predict,
        contents
    )
    return result
```

## 11. Testing FastAPI Applications

### 11.1 TestClient

FastAPI provides a test client:

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### 11.2 Testing File Uploads

```python
def test_predict():
    with open("test_image.jpg", "rb") as f:
        response = client.post(
            "/predict",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    assert response.status_code == 200
    assert "detections" in response.json()
```

## 12. Production Considerations

### 12.1 ASGI Servers

FastAPI requires an ASGI server:
- **Uvicorn**: Lightweight, fast, recommended for development
- **Gunicorn + Uvicorn**: Production setup with worker management
- **Hypercorn**: Alternative ASGI server

Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 12.2 Environment Configuration

Use environment variables for configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_path: str = "yolov5s.pt"
    max_file_size: int = 10_000_000  # 10MB

    class Config:
        env_file = ".env"

settings = Settings()
```

### 12.3 Logging

Implement structured logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    logger.info(f"Processing file: {file.filename}")
    # Process
    logger.info("Prediction complete")
```

## 13. Performance Optimization

### 13.1 Response Compression

Enable gzip compression:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 13.2 Caching

Implement result caching for repeated requests:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_prediction(image_hash: str):
    # Return cached result
    pass
```

### 13.3 Request Limits

Prevent large uploads:

```python
from fastapi import Request

@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.headers.get("content-length"):
        if int(request.headers["content-length"]) > 10_000_000:
            raise HTTPException(413, "File too large")
    return await call_next(request)
```

## 14. Summary

FastAPI provides a robust foundation for deploying machine learning models through:
- Type-safe request handling
- Automatic validation and documentation
- High-performance asynchronous processing
- Production-ready features (CORS, middleware, testing)

The combination of these features makes FastAPI particularly suitable for ML deployment where:
- Input validation is critical (wrong data types can crash models)
- Documentation aids client integration
- Performance impacts user experience
- Production reliability is essential

## Next Steps

Proceed to [Docker Guide](02_docker_guide.md) to learn containerization of this FastAPI application.
