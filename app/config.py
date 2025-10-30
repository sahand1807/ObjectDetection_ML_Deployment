"""
Configuration Management for the API

This file stores all the settings for our application in one place.
Using Pydantic's BaseSettings gives us:
1. Type validation (ensures values are correct types)
2. Environment variable support (can override settings with ENV vars)
3. Default values (fallback if not specified)
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings that can be configured via environment variables

    Example: Set MODEL_NAME=yolov8n.pt in a .env file to use a different model
    """

    # API Metadata
    app_name: str = "Object Detection API"
    app_version: str = "1.0.0"

    # Model Configuration
    model_name: str = "yolov8n.pt"  # 'n' = nano (smallest, fastest)
    confidence_threshold: float = 0.5  # Minimum confidence to show detection (0-1)
    iou_threshold: float = 0.45  # Intersection over Union for removing duplicate boxes

    # File Upload Limits
    max_file_size: int = 10_000_000  # 10MB in bytes
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "bmp", "webp"]

    # Server Configuration
    host: str = "0.0.0.0"  # Listen on all network interfaces
    port: int = 8000

    # CORS (Cross-Origin Resource Sharing) - needed for web browser access
    # ["*"] means allow all origins - restrict this in production!
    cors_origins: List[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Create a single instance that we'll import everywhere
# This is called the "Singleton pattern" - only one Settings object exists
settings = Settings()
