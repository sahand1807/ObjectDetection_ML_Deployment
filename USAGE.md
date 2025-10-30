# Usage Guide

## Quick Start

### 1. Local Development

Start the server:
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser:
- **Demo UI**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Using Docker

```bash
# Build the image
docker build -t object-detection-api .

# Run the container
docker run -p 8000:8000 object-detection-api

# Or use docker-compose
docker-compose up
```

## Demo Interface

The visual demo interface is available at the root URL (`/`).

### Features:
- **Drag & Drop Upload**: Click or drag images to upload
- **Confidence Threshold**: Adjust minimum confidence (0-1) for detections
- **IoU Threshold**: Control duplicate box removal (0-1)
- **Visual Results**: See bounding boxes drawn on your image
- **Detailed Stats**: View inference time, object counts, and more

### What is IoU?
**IoU (Intersection over Union)** removes duplicate detections of the same object:
- **Lower values (0.3)**: More aggressive - removes more duplicates
- **Default (0.45)**: Balanced - good for most cases
- **Higher values (0.7)**: Less aggressive - might keep duplicates

### Supported Image Formats:
- JPG/JPEG
- PNG
- BMP
- WebP
- Maximum size: 10MB

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "yolov8n.pt",
  "version": "1.0.0"
}
```

### Object Detection

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@image.jpg" \
  -F "confidence=0.5" \
  -F "iou_threshold=0.45"
```

Response:
```json
{
  "detections": [
    {
      "class_name": "person",
      "confidence": 0.85,
      "bbox": {
        "x_min": 100,
        "y_min": 150,
        "x_max": 400,
        "y_max": 500
      }
    }
  ],
  "num_detections": 1,
  "inference_time_ms": 120.5,
  "image_dimensions": [1920, 1080],
  "model_name": "yolov8n.pt"
}
```

### Query Parameters

- `confidence` (optional): Minimum confidence threshold (0.0-1.0, default: 0.5)
- `iou_threshold` (optional): IoU threshold for NMS (0.0-1.0, default: 0.45)

## Python Client Example

```python
import requests

# Upload and detect
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    params = {'confidence': 0.6, 'iou_threshold': 0.45}
    response = requests.post(
        'http://localhost:8000/predict',
        files=files,
        params=params
    )

result = response.json()
print(f"Found {result['num_detections']} objects")
for detection in result['detections']:
    print(f"- {detection['class_name']}: {detection['confidence']:.2%}")
```

## JavaScript Client Example

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/predict?confidence=0.6', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(`Found ${data.num_detections} objects`);
    data.detections.forEach(det => {
        console.log(`${det.class_name}: ${det.confidence}`);
    });
});
```

## Environment Configuration

Create a `.env` file to customize settings:

```bash
# Copy example
cp .env.example .env

# Edit with your preferences
nano .env
```

Available settings:
- `MODEL_NAME`: YOLO model to use (yolov8n.pt, yolov8s.pt, etc.)
- `CONFIDENCE_THRESHOLD`: Default confidence threshold
- `IOU_THRESHOLD`: Default IoU threshold
- `MAX_FILE_SIZE`: Maximum upload size in bytes
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins

## YOLO Models

Available models (from fastest to most accurate):

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| yolov8n.pt | 6MB | Fastest | Good |
| yolov8s.pt | 22MB | Fast | Better |
| yolov8m.pt | 52MB | Medium | Great |
| yolov8l.pt | 87MB | Slow | Excellent |
| yolov8x.pt | 136MB | Slowest | Best |

The model will auto-download on first use.

## Detected Object Classes

YOLO can detect 80 different classes:
- **People**: person
- **Vehicles**: bicycle, car, motorcycle, airplane, bus, train, truck, boat
- **Animals**: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
- **Objects**: backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, skateboard, surfboard, tennis racket
- **Food**: bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake
- **Furniture**: chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone
- **Appliances**: microwave, oven, toaster, sink, refrigerator
- **Indoor**: book, clock, vase, scissors, teddy bear, hair drier, toothbrush

## Troubleshooting

### Model not loading
- Check internet connection (model downloads from GitHub)
- Ensure write permissions in the app directory
- Try manually downloading the model file

### Slow inference
- Use a smaller model (yolov8n.pt instead of yolov8x.pt)
- Resize images before uploading
- Ensure adequate CPU/RAM

### No objects detected
- Lower the confidence threshold
- Try a different image
- Check image quality and size

### CORS errors
- Add your domain to `CORS_ORIGINS` in settings
- For development, use `["*"]` to allow all origins

## Performance Tips

1. **Use GPU** (if available):
   - Install CUDA-enabled PyTorch
   - Model will automatically use GPU

2. **Batch processing**:
   - Process multiple images in a loop
   - Model stays loaded in memory

3. **Optimize for production**:
   - Use Gunicorn with multiple workers
   - Enable response compression
   - Cache frequently processed images

## Next Steps

- See [Deployment Guide](docs/03_deployment_guide.md) for cloud deployment
- See [Hugo Integration](docs/04_hugo_integration.md) for website integration
- Check the [FastAPI docs](http://localhost:8000/docs) for interactive testing
