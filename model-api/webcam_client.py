#!/usr/bin/env python3
"""
Lightweight Webcam Client for Stream2Prompt Model API

Captures frames from webcam and sends them to the Model API at configurable FPS.
"""

import cv2
import requests
import time
import argparse

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default configuration - modify these values as needed
DEFAULT_FPS = 10                                    # Frames per second to send to API
DEFAULT_ENDPOINT = "http://localhost:8000"          # Model API endpoint
DEFAULT_INPUT_SOURCE = 0                            # Webcam index (0 = default camera)

# Network configuration
REQUEST_TIMEOUT = 5.0                               # Timeout for API requests (seconds)

# Video configuration
JPEG_QUALITY = 80                                   # JPEG compression quality (1-100)

# =============================================================================
# API COMMUNICATION
# =============================================================================

def send_frame_to_api(frame, endpoint: str) -> bool:
    """
    Send a frame to the Model API for prediction.
    
    Args:
        frame: OpenCV frame (numpy array)
        endpoint: API endpoint URL
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        
        # Prepare the file for upload
        files = {'image': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
        
        # Send POST request to /predict/
        response = requests.post(
            f"{endpoint}/predict/",
            files=files,
            timeout=REQUEST_TIMEOUT
        )
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"Error sending frame: {e}")
        return False

# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_webcam(fps: int, input_source, endpoint: str):
    """
    Main webcam processing function.
    
    Args:
        fps: Target frames per second
        input_source: Video input source (camera index or file path)
        endpoint: Model API endpoint
    """
    # Initialize video capture
    cap = cv2.VideoCapture(input_source)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source {input_source}")
        return
    
    print(f"Capturing from source {input_source} at {fps} FPS")
    print(f"Sending frames to {endpoint}/predict/")
    print("Press Ctrl+C to stop")
    
    # Calculate frame interval
    frame_interval = 1.0 / fps
    last_send_time = 0
    frame_count = 0
    successful_sends = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame from camera")
                break
            
            current_time = time.time()
            frame_count += 1
            
            # Send frame to API at specified FPS
            if current_time - last_send_time >= frame_interval:
                success = send_frame_to_api(frame, endpoint)
                if success:
                    successful_sends += 1
                    last_send_time = current_time
                    
                    # Print progress every 50 successful sends
                    if successful_sends % 50 == 0:
                        elapsed = current_time - start_time
                        actual_fps = successful_sends / elapsed
                        print(f"Sent {successful_sends} frames in {elapsed:.1f}s (avg {actual_fps:.1f} FPS)")
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    finally:
        cap.release()
        
        # Print statistics
        elapsed_time = time.time() - start_time
        actual_fps = successful_sends / elapsed_time if elapsed_time > 0 else 0
        success_rate = (successful_sends / frame_count * 100) if frame_count > 0 else 0
        
        print("\nStatistics:")
        print(f"  Frames captured: {frame_count}")
        print(f"  Frames sent successfully: {successful_sends}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Average send rate: {actual_fps:.1f} FPS")
        print(f"  Duration: {elapsed_time:.1f} seconds")

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function with command line argument parsing."""
    
    parser = argparse.ArgumentParser(description='Lightweight Webcam Client for Stream2Prompt Model API')
    parser.add_argument('--fps', type=int, default=DEFAULT_FPS,
                       help=f'Frames per second to send to API (default: {DEFAULT_FPS})')
    parser.add_argument('--endpoint', type=str, default=DEFAULT_ENDPOINT,
                       help=f'Model API endpoint URL (default: {DEFAULT_ENDPOINT})')
    parser.add_argument('--input', type=str, default=str(DEFAULT_INPUT_SOURCE),
                       help=f'Input source: camera index or video file path (default: {DEFAULT_INPUT_SOURCE})')
    
    args = parser.parse_args()
    
    # Convert input source to integer if it's a camera index
    input_source = args.input
    try:
        input_source = int(args.input)
    except ValueError:
        pass  # Keep as string (file path)
    
    print("Stream2Prompt Webcam Client (Lightweight)")
    print("=" * 50)
    print(f"FPS: {args.fps}")
    print(f"Endpoint: {args.endpoint}")
    print(f"Input Source: {input_source}")
    print("=" * 50)
    
    # Test API connectivity
    try:
        response = requests.get(f"{args.endpoint}/", timeout=5)
        if response.status_code == 200:
            print("✓ API connection successful")
        else:
            print("⚠ API responded but with unexpected status code")
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        print("Make sure the Model API is running!")
        return
    
    # Start main processing
    try:
        process_webcam(
            fps=args.fps,
            input_source=input_source,
            endpoint=args.endpoint
        )
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()