"""
FastAPI Application - Main Entry Point

This file creates the API server and defines all endpoints (routes).

Endpoints we'll create:
1. GET /health - Check if the API is running
2. POST /predict - Upload image, get object detections
3. GET / - Root endpoint with API info

Key Concepts:
- @app.on_event("startup") runs once when server starts
- @app.get() and @app.post() create API endpoints
- Type hints automatically validate inputs
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

from app.config import settings
from app.models import HealthResponse, PredictionResponse
from app.inference import detector

# Set up logging (prints messages to console)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
# This is the core object that handles all HTTP requests
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Upload an image and receive object detection results with bounding boxes",
    # Auto-generated docs will be at: http://localhost:8000/docs
)

# Add CORS middleware
# CORS = Cross-Origin Resource Sharing
# This allows your Hugo website (different domain) to call this API
# Without CORS, browsers block requests from different origins (security feature)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Which domains can access (["*"] = all)
    allow_credentials=True,
    allow_methods=["*"],  # Which HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Which headers are allowed
)

# Mount static files (for demo UI)
# This serves the HTML/CSS/JS files from the static directory
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# Startup Event - runs ONCE when the server starts
@app.on_event("startup")
async def startup_event():
    """
    Initialize resources when the application starts

    This is crucial for ML deployment:
    - Load the model ONCE at startup (not on every request)
    - Loading takes a few seconds, but we only do it once
    - The model stays in memory for all requests
    """
    logger.info("=" * 50)
    logger.info("Starting Object Detection API")
    logger.info("=" * 50)

    # Load the YOLO model
    success = detector.load_model()

    if not success:
        logger.error("Failed to load model! API will not work properly.")
    else:
        logger.info(f"Model loaded: {settings.model_name}")
        logger.info(f"Server running on http://{settings.host}:{settings.port}")
        logger.info(f"API Documentation: http://localhost:{settings.port}/docs")
        logger.info("=" * 50)


# Root Endpoint - Serve demo UI
@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint - serves the demo UI

    Try it: Open http://localhost:8000/ in your browser
    """
    index_path = Path(__file__).parent.parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        # Fallback if static files not available
        return {
            "message": "Object Detection API",
            "version": settings.app_version,
            "docs": "/docs",
            "demo": "Demo UI not available (static files missing)",
            "endpoints": {
                "health": "GET /health - Check API status",
                "predict": "POST /predict - Detect objects in an image",
            },
        }


# Health Check Endpoint
@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint

    Purpose:
    - Verify the API is running
    - Check if the ML model is loaded
    - Used by monitoring tools and cloud platforms

    In production, cloud services ping this endpoint to ensure the app is alive
    """
    is_healthy = detector.is_loaded()

    return HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        model_loaded=is_healthy,
        model_name=settings.model_name,
        version=settings.app_version,
    )


# Object Detection Endpoint - THE MAIN FEATURE
@app.post("/predict", response_model=PredictionResponse, tags=["Object Detection"])
async def predict_objects(
    file: UploadFile = File(..., description="Image file (JPG, PNG, etc.)"),
    confidence: float = Query(
        None, ge=0.0, le=1.0, description="Confidence threshold (0-1). Default: 0.5"
    ),
    iou_threshold: float = Query(
        None, ge=0.0, le=1.0, description="IoU threshold for NMS (0-1). Default: 0.45"
    ),
):
    """
    Detect objects in an uploaded image

    How to use:
    1. POST request to /predict
    2. Include image file in form-data with key "file"
    3. Optional: Add query parameters ?confidence=0.7&iou_threshold=0.5

    What you get back:
    - List of detected objects (class name, confidence, bounding box)
    - Inference time (how long the detection took)
    - Image dimensions

    Example using curl:
    ```
    curl -X POST "http://localhost:8000/predict?confidence=0.6" \\
         -F "file=@your_image.jpg"
    ```

    Parameters:
    - file: The image to analyze
    - confidence: Minimum confidence to include a detection (higher = fewer but more certain results)
    - iou_threshold: Controls how much boxes can overlap before removing duplicates
    """

    # Validate model is loaded
    if not detector.is_loaded():
        logger.error("Prediction attempted but model not loaded")
        raise HTTPException(status_code=503, detail="Model not loaded. Service unavailable.")

    # Validate file type
    # content_type tells us the file format (image/jpeg, image/png, etc.)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail=f"File must be an image. Got: {file.content_type}"
        )

    # Validate file extension
    file_ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{file_ext} not allowed. Allowed: {settings.allowed_extensions}",
        )

    try:
        # Read the uploaded file into memory
        # This reads the entire file as bytes
        image_bytes = await file.read()

        # Check file size
        if len(image_bytes) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_file_size / 1_000_000}MB",
            )

        logger.info(f"Processing image: {file.filename} ({len(image_bytes)} bytes)")

        # Run object detection
        # This is where the magic happens!
        result = detector.predict(
            image_bytes=image_bytes, confidence_threshold=confidence, iou_threshold=iou_threshold
        )

        logger.info(
            f"Detection complete: {result.num_detections} objects found in {result.inference_time_ms:.2f}ms"
        )

        return result

    except HTTPException:
        # Re-raise HTTP exceptions (already handled above)
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Error during prediction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch-all error handler

    If something goes wrong that we didn't anticipate,
    this returns a proper JSON error instead of crashing
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error", "error": str(exc)}
    )