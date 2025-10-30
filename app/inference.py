"""
Model Inference Logic

This module handles:
1. Loading the YOLO model into memory
2. Processing uploaded images
3. Running object detection
4. Formatting results for the API

The model is only laoded ONCE when the app starts, not on every request.
This saves time since model loading is expensive (takes a few seconds).
"""

import time
from typing import List
from PIL import Image
import io
import numpy as np
from ultralytics import YOLO

from app.models import Detection, BoundingBox, PredictionResponse
from app.config import settings


class ObjectDetector:
    """
    Manages the YOLO model and performs object detection

    This class follows the Singleton pattern - we create ONE instance
    when the app starts and reuse it for all requests.
    """

    def __init__(self):
        """
        Initialize the detector (called once at startup)
        """
        self.model = None
        self.model_name = settings.model_name
        print(f"Initializing ObjectDetector with model: {self.model_name}")

    def load_model(self):
        """
        Load the YOLO model into memory

        YOLO (You Only Look Once) is a fast object detection model.
        The first time this runs, it will download the model weights (~6MB for nano).

        Model sizes (speed vs accuracy tradeoff):
        - yolov8n.pt (nano): Fastest, least accurate
        - yolov8s.pt (small): Balanced
        - yolov8m.pt (medium): More accurate, slower
        - yolov8l.pt (large): Very accurate, much slower
        """
        try:
            print(f"Loading YOLO model: {self.model_name}")
            # Ultralytics will auto-download the model if not present
            self.model = YOLO(self.model_name)
            print(f"✓ Model loaded successfully!")
            return True
        except Exception as e:
            print(f"✗ Error loading model: {str(e)}")
            return False

    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None

    def process_image(self, image_bytes: bytes) -> Image.Image:
        """
        Convert uploaded bytes to a PIL Image

        PIL (Python Imaging Library) is the standard library for image processing
        io.BytesIO creates a file-like object from bytes (so PIL can read it)
        """
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed (some images are RGBA or grayscale)
        if image.mode != "RGB":
            image = image.convert("RGB")

        return image

    def predict(
        self, image_bytes: bytes, confidence_threshold: float = None, iou_threshold: float = None
    ) -> PredictionResponse:
        """
        Run object detection on an image

        Args:
            image_bytes: Raw image data from the upload
            confidence_threshold: Minimum confidence to include detection (0-1)
            iou_threshold: IoU threshold for Non-Maximum Suppression (removes duplicate boxes)

        Returns:
            PredictionResponse with all detected objects

        How it works:
        1. Convert bytes to image
        2. Pass image through YOLO model
        3. Filter results by confidence
        4. Format into our API response structure
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Use settings defaults if not provided
        if confidence_threshold is None:
            confidence_threshold = settings.confidence_threshold
        if iou_threshold is None:
            iou_threshold = settings.iou_threshold

        # Process image
        image = self.process_image(image_bytes)
        image_width, image_height = image.size

        # Run inference and time it
        start_time = time.time()

        # YOLO inference
        # conf: minimum confidence
        # iou: IoU threshold for NMS (Non-Maximum Suppression)
        # verbose: don't print progress
        results = self.model.predict(source=image, conf=confidence_threshold, iou=iou_threshold, verbose=False)

        inference_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Parse results
        detections = self._parse_results(results[0])

        # Build response
        response = PredictionResponse(
            detections=detections,
            num_detections=len(detections),
            inference_time_ms=round(inference_time, 2),
            image_dimensions=(image_width, image_height),
            model_name=self.model_name,
        )

        return response

    def _parse_results(self, result) -> List[Detection]:
        """
        Convert YOLO results to our Detection format

        YOLO returns results in a specific format:
        - boxes.xyxy: bounding box coordinates [x_min, y_min, x_max, y_max]
        - boxes.conf: confidence scores
        - boxes.cls: class indices (0=person, 1=bicycle, 2=car, etc.)

        We convert this to our clean API format
        """
        detections = []

        # Get detections (may be empty if nothing found)
        if result.boxes is None or len(result.boxes) == 0:
            return detections

        # Extract data from YOLO result
        boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes
        confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
        class_ids = result.boxes.cls.cpu().numpy().astype(int)  # Class IDs

        # Get class names (YOLO has 80 classes like 'person', 'car', 'dog', etc.)
        class_names = result.names  # Dictionary: {0: 'person', 1: 'bicycle', ...}

        # Build Detection objects
        for box, conf, cls_id in zip(boxes, confidences, class_ids):
            detection = Detection(
                class_name=class_names[cls_id],
                confidence=float(conf),
                bbox=BoundingBox(
                    x_min=int(box[0]),
                    y_min=int(box[1]),
                    x_max=int(box[2]),
                    y_max=int(box[3]),
                ),
            )
            detections.append(detection)

        return detections


# Global instance - created once, used by all requests
# This is initialized when the FastAPI app starts
detector = ObjectDetector()