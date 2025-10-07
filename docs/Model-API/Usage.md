# Model API Usage Guide

This document provides comprehensive usage instructions for the Stream2Prompt Model API, a FastAPI-based object detection service using YOLO11.

## Overview

The Model API provides real-time object detection capabilities through a RESTful interface. It uses an asynchronous prediction system where images are processed in a background thread, allowing for efficient handling of multiple requests.

## Starting the API Server

Run the API server using UV:

```bash
uv run fastapi run model-api/model-api.py
```

The server will start on `http://localhost:8000` by default.

## API Endpoints

### 1. Root Endpoint - Health Check

**GET** `/`

Returns detection results from a random warmup image (used for testing/health check).

#### Response Format:
```json
{
  "detections": [
    {
      "class_name": "person",
      "confidence": 0.95
    }
  ]
}
```

### 2. Upload Image for Prediction

**POST** `/predict/`

Uploads an image for object detection. The image is processed asynchronously in a background thread.

#### Request:
- **Content-Type**: `multipart/form-data`
- **Parameter**: `image` (file upload)

#### Supported Image Formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

#### Example using cURL:
```bash
curl -X POST "http://localhost:8000/predict/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@path/to/your/image.jpg"
```

#### Response:
```json
{
  "status": "Image received for prediction"
}
```

### 3. Get Prediction Results

**GET** `/result/`

Retrieves the latest prediction results with detailed detection information.

#### Response Format (Successful Detection):
```json
{
  "detections": [
    {
      "class_name": "person",
      "confidence": 0.95,
      "bbox": [100, 50, 200, 300]
    },
    {
      "class_name": "car",
      "confidence": 0.87,
      "bbox": [300, 100, 500, 250]
    }
  ],
  "timestamp": 1696780800.123,
  "total_objects": 2
}
```

#### Response Format (No Objects Detected):
```json
{
  "detections": [],
  "timestamp": 1696780800.123,
  "total_objects": 0,
  "message": "No objects detected in the image"
}
```

#### Response Format (No Prediction Available):
```json
{
  "detections": [],
  "timestamp": null,
  "message": "No prediction available yet"
}
```

## Response Fields Explained

### Detection Object:
- **`class_name`**: Human-readable name of the detected object class
- **`confidence`**: Detection confidence score (0.0 to 1.0)
- **`bbox`**: Bounding box coordinates as `[x1, y1, x2, y2]` where:
  - `x1, y1`: Top-left corner coordinates
  - `x2, y2`: Bottom-right corner coordinates

### Additional Fields:
- **`timestamp`**: Unix timestamp when the prediction was completed
- **`total_objects`**: Total number of detected objects
- **`message`**: Status or informational message (when applicable)

## Usage Workflow

### Basic Usage Pattern:
1. **Upload Image**: Send POST request to `/predict/` with your image
2. **Poll Results**: Send GET requests to `/result/` to retrieve detection results
3. **Process Results**: Use the returned detection data for your application

### Example Python Client:

```python
import requests
import json
import time

# Upload image for prediction
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict/',
        files={'image': f}
    )
    print(f"Upload status: {response.json()}")

# Wait a moment for processing
time.sleep(1)

# Get prediction results
result = requests.get('http://localhost:8000/result/')
data = result.json()

print(f"Detected {data['total_objects']} objects:")
for detection in data['detections']:
    print(f"- {detection['class_name']}: {detection['confidence']:.2f} confidence")
    print(f"  Location: {detection['bbox']}")
```

### Example JavaScript Client:

```javascript
// Upload image for prediction
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8000/predict/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log('Upload status:', data));

// Get prediction results (after a brief delay)
setTimeout(() => {
    fetch('http://localhost:8000/result/')
    .then(response => response.json())
    .then(data => {
        console.log(`Detected ${data.total_objects} objects:`);
        data.detections.forEach(detection => {
            console.log(`${detection.class_name}: ${detection.confidence.toFixed(2)} confidence`);
        });
    });
}, 1000);
```

## Features

### Asynchronous Processing:
- Images are processed in a background thread
- Non-blocking API responses
- Efficient handling of multiple requests

### Sorted Results:
- Detections are automatically sorted by confidence in descending order
- Highest confidence detections appear first

### Comprehensive Detection Data:
- Class names for human readability
- Confidence scores for reliability assessment
- Bounding box coordinates for spatial information
- Timestamps for temporal tracking

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: Visit `http://localhost:8000/docs`
- **ReDoc**: Visit `http://localhost:8000/redoc`

These interfaces allow you to test the API endpoints directly from your browser.

## Error Handling

The API handles various edge cases:

- **No prediction available**: Returns empty detections with appropriate message
- **No objects detected**: Returns empty detections with timestamp
- **Invalid image format**: FastAPI will return appropriate HTTP error codes
- **Missing image parameter**: Returns validation error

## Performance Considerations

- **Model Loading**: The YOLO model is loaded once at startup with warmup
- **Background Processing**: Predictions run in a separate thread to avoid blocking
- **Memory Management**: Only the latest prediction is kept in memory
- **Response Time**: Initial model loading takes time; subsequent predictions are faster

## Troubleshooting

### Common Issues:

1. **Model not found**: Ensure `model-lab/yolo11/best.engine` exists
2. **Slow responses**: First prediction includes model loading time
3. **Memory issues**: Large images may require more system memory
4. **Port conflicts**: Change the default port if 8000 is in use

### Debug Information:
Check the server logs for detailed error messages and processing information.
