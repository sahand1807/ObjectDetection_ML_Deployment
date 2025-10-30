"""
Data Models (Schemas) for API Requests and Responses

Pydantic models serve three purposes:
1. Validation: Ensures data has the correct structure and types
2. Documentation: Auto-generates API documentation showing expected formats
3. Serialization: Converts Python objects to JSON and vice versa

These are "blueprints" for the data structure
"""

from pydantic import BaseModel, Field
from typing import List, Tuple


class BoundingBox(BaseModel):
    """
    Represents a rectangular box around a detected object

    Coordinates are in pixels:
    - x_min: left edge
    - y_min: top edge
    - x_max: right edge
    - y_max: bottom edge

    Example: {"x_min": 100, "y_min": 150, "x_max": 400, "y_max": 500}
    """

    x_min: int = Field(..., description="Left x coordinate in pixels")
    y_min: int = Field(..., description="Top y coordinate in pixels")
    x_max: int = Field(..., description="Right x coordinate in pixels")
    y_max: int = Field(..., description="Bottom y coordinate in pixels")


class Detection(BaseModel):
    """
    A single detected object with its properties

    Example:
    {
        "class_name": "person",
        "confidence": 0.95,
        "bbox": {"x_min": 100, "y_min": 150, "x_max": 400, "y_max": 500}
    }
    """

    class_name: str = Field(..., description="Name of the detected object (e.g., 'car', 'person')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")


class PredictionResponse(BaseModel):
    """
    Complete API response containing all detections

    This is what the client receives after uploading an image
    """

    detections: List[Detection] = Field(..., description="List of all detected objects")
    num_detections: int = Field(..., description="Total number of objects detected")
    inference_time_ms: float = Field(..., description="Time taken for inference in milliseconds")
    image_dimensions: Tuple[int, int] = Field(..., description="Original image size (width, height)")
    model_name: str = Field(..., description="Name of the model used")

    model_config = {
        "json_schema_extra": {
            "example": {
                "detections": [
                    {
                        "class_name": "person",
                        "confidence": 0.92,
                        "bbox": {"x_min": 120, "y_min": 80, "x_max": 320, "y_max": 450},
                    },
                    {
                        "class_name": "car",
                        "confidence": 0.87,
                        "bbox": {"x_min": 500, "y_min": 200, "x_max": 800, "y_max": 400},
                    },
                ],
                "num_detections": 2,
                "inference_time_ms": 145.3,
                "image_dimensions": [1920, 1080],
                "model_name": "yolov8n.pt",
            }
        }
    }


class HealthResponse(BaseModel):
    """
    Health check response - tells us if the API is running correctly
    """

    status: str = Field(..., description="API status (healthy/unhealthy)")
    model_loaded: bool = Field(..., description="Whether ML model is loaded in memory")
    model_name: str = Field(..., description="Name of the loaded model")
    version: str = Field(..., description="API version")