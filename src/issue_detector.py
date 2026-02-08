import pathlib
import time
import cv2
import os
import torch
import multiprocessing
import logging

from huggingface_hub import hf_hub_download

from src.config import get_config
from src.notifier import send_notification # Import send_notification

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _load_model():
    model_cache = pathlib.Path(__file__).parent.resolve().joinpath("../model")

    try:
        model_path = hf_hub_download(
            repo_id="Javiai/3dprintfails-yolo5vs",
            filename="model_torch.pt",
            local_dir=model_cache,
        )
        return torch.hub.load('Ultralytics/yolov5', 'custom', model_path, verbose=False)

    except Exception as e:
        logger.error(f"Error loading ML model: {e}")
        raise

def _detect_issues_process(terminate_event: multiprocessing.Event):
    """
    Worker function for the issue detection process.
    It manages the video stream, captures frames, runs inference, and sends notifications directly.
    The process runs continuously until a terminate_event is set.
    """
    config = get_config()['issue_detector']

    stream_url = config['stream_url']
    confidence_thresholds = config['confidence_thresholds']

    model = _load_model()

    cap = None
    last_inference_time = 0
    last_issue_reported_time = 0

    try:
        while not terminate_event.is_set():
            # Open camera if not already open or if it was closed
            if cap is None or not cap.isOpened():
                os.environ['OPENCV_FFMPEG_LOGLEVEL'] = 'quiet'
                cap = cv2.VideoCapture(stream_url)
                if not cap.isOpened():
                    logger.error(f"Could not open video stream from {stream_url}. Retrying in 5 seconds...")
                    time.sleep(5) # Wait before retrying
                    continue # Skip to next loop iteration

            ret, frame = cap.read()

            if not ret:
                logger.error("Failed to read frame from stream. Reconnecting in 5 seconds...")
                if cap is not None and cap.isOpened():
                    cap.release()
                cap = None # Reset cap to force re-opening
                time.sleep(5)
                continue

            current_time = time.time()
            if current_time - last_inference_time >= 5: # Process frame every 5 seconds
                results = model(frame)
                detections = results.pandas().xyxy[0].to_dict(orient="records")
                filtered_detections = []

                for detection in detections:
                    class_name = detection['name']
                    confidence = detection['confidence']
                    threshold = confidence_thresholds.get(class_name, 1.0)
                    if class_name in confidence_thresholds:  # Just for logging.
                        logger.info(f"Detected {class_name} with confidence {confidence:.2f}")
                    if confidence > threshold:
                        filtered_detections.append(detection)

                for detection in filtered_detections:
                    class_name = detection['name']
                    confidence = detection['confidence']

                    message = f"Detected '{class_name}' with confidence {confidence:.2f}"
                    logger.info(f"{message}")
                    if current_time - last_issue_reported_time >= 60:  # Limit to 1 message per minute.
                        send_notification(message)
                        last_issue_reported_time = current_time
                last_inference_time = current_time

            time.sleep(0.05) # Small delay to prevent busy-waiting

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Worker stopping.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        if cap is not None and cap.isOpened():
            cap.release()
        logger.info("Video stream released and worker finished.")

def start_issue_detector_process():
    """
    Initializes and starts the issue detection process.
    Returns the process object and the terminate_event.
    """
    terminate_event = multiprocessing.Event()
    process = multiprocessing.Process(target=_detect_issues_process, args=(terminate_event,))
    process.start()
    return process, terminate_event

if __name__ == '__main__':
    logger.info("[Main] Starting issue detector controller.")

    try:
        detector_process, terminate_event = start_issue_detector_process()
        time.sleep(60) # Run for a fixed duration for testing this simplified model
    finally:
        terminate_event.set() # Signal the worker to stop completely
        detector_process.join(timeout=10) # Wait for worker to finish gracefully
