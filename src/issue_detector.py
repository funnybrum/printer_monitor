import pathlib
import time
import cv2
import os
import multiprocessing
import logging
import numpy as np
from openvino import Core, Layout

from src.config import get_config
from src.notifier import send_notification # Import send_notification

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLDS = get_config()['issue_detector']['confidence_thresholds']
MODEL_CLASS_NAMES = {
    0: 'error',
    1: 'extrusor',
    2: 'part',
    3: 'spaghetti'
}

def _pre_process_detection_results(detection_results):
    """
    1. Process detections and apply the thresholds
    2. Apply non-maximum suppression
    3. Provide simple list of (class_name, confidence_score) pairs as result.
    """
    boxes = []
    confidences = []
    class_ids = []

    # Loop through detections
    for detection in detection_results:
        #  Each detection is an array of numbers. The numbers specify the location of the object and the
        #  confidence scores for each detected object:
        # (center_x, center_y, w, h, objectness_score, class_0_score, class_1_score, class_2_score, ...)
        # Score for "spaghetti" would be class_3_score * objectness_score.

        # Extract objectness score and class confidences
        objectness_score = detection[4]
        class_confidences = detection[5:]

        # Determine the class ID and its confidence
        class_id_raw = np.argmax(class_confidences)
        max_class_confidence = class_confidences[class_id_raw]

        # Combine objectness and class confidence for the final confidence score
        confidence = objectness_score * max_class_confidence

        class_name = MODEL_CLASS_NAMES.get(class_id_raw, f"unknown_class_{class_id_raw}")

        # Confidence score as specified or 1 to filter out objects we don't care about.
        threshold = CONFIDENCE_THRESHOLDS.get(class_name, 1.0)

        if confidence > threshold:
            boxes.append(detection[0:4])
            confidences.append(float(confidence))
            class_ids.append(class_id_raw)

    # Apply Non-Maximum Suppression
    NMS_IOU_THRESHOLD = 0.4

    # The confidence score criteria was already applied above
    NMS_SCORE_THRESHOLD = 0

    indices = cv2.dnn.NMSBoxes(boxes, confidences, NMS_SCORE_THRESHOLD, NMS_IOU_THRESHOLD)

    filtered_detections = []
    if len(indices) > 0:
        for i in indices.flatten():
            class_id_retained = class_ids[i]
            confidence_retained = confidences[i]
            class_name_retained = MODEL_CLASS_NAMES.get(class_id_retained)

            filtered_detections.append({
                "name": class_name_retained,
                "confidence": confidence_retained,
            })

    return filtered_detections


def _detect_issues_process(terminate_event: multiprocessing.Event):
    """
    Worker function for the issue detection process.
    It manages the video stream, captures frames, runs inference, and sends notifications directly.
    The process runs continuously until a terminate_event is set.
    """
    config = get_config()['issue_detector']

    stream_url = config['stream_url']

    model_xml_path = pathlib.Path(__file__).parent.resolve().parent.joinpath('model/model_torch.xml')

    if not model_xml_path.exists():
        logger.error(f"OpenVINO model not found at {model_xml_path}.")
        raise FileNotFoundError(f"OpenVINO model files not found.")

    logger.info(f"Loading OpenVINO model from {model_xml_path}")
    core = Core()
    model = core.read_model(model_xml_path)
    compiled_model = core.compile_model(model, "GPU")

    # Assuming model input name and shape
    input_layer = compiled_model.input(0)
    output_layer = compiled_model.output(0)

    # Get input shape and resize accordingly
    # OpenVINO model input shape is usually [1, 3, H, W] for NCHW layout
    _, _, input_height, input_width = input_layer.shape

    cap = None
    # Inference reduced to 1 per 5 seconds to reduce CPU load.
    last_inference_time = 0

    # Issues reported once per 60 seconds to avoid constant spam.
    last_issue_reported_time = 0

    try:
        while not terminate_event.is_set():
            current_time = time.time()
            # Open camera if not already open or if it was closed
            if cap is None or not cap.isOpened():
                os.environ['OPENCV_FFMPEG_LOGLEVEL'] = 'quiet'
                cap = cv2.VideoCapture(stream_url)
                if not cap.isOpened():
                    logger.error(f"Could not open video stream from {stream_url}. Retrying in 5 seconds...")
                    if current_time - last_issue_reported_time >= 60:
                        send_notification("Failed to open video stream")
                        last_issue_reported_time = current_time
                    time.sleep(5) # Wait before retrying
                    continue # Skip to next loop iteration

            ret, frame = cap.read()

            if not ret:
                logger.error("Failed to read frame from stream. Reconnecting in 5 seconds...")
                if current_time - last_issue_reported_time >= 60:
                    send_notification("Failed to read from video stream")
                    last_issue_reported_time = current_time
                if cap is not None and cap.isOpened():
                    cap.release()
                cap = None # Reset cap to force re-opening
                time.sleep(5)
                continue

            if current_time - last_inference_time >= 5: # Process frame every 5 seconds
                # Pre-process frame for OpenVINO model
                # 1. Resize to model input size (input_width, input_height)
                resized_frame = cv2.resize(frame, (input_width, input_height))

                # 2. Convert HWC to CHW (channels first)
                input_frame = resized_frame.transpose((2, 0, 1))

                # 3. Add batch dimension
                input_frame = input_frame[None, :, :, :]

                # 4. Normalize pixel values to [0, 1] and convert to float32
                input_frame = input_frame.astype(float) / 255.0

                # 5. Perform inference using OpenVINO compiled model
                results_ov = compiled_model([input_frame])[output_layer]

                # 6. Pre-process detection results
                filtered_detections = _pre_process_detection_results(results_ov[0])

                # 7. Sends notifications
                for detection in filtered_detections:
                    class_name = detection['name']
                    confidence = detection['confidence']

                    message = f"Detected '{class_name}' with confidence {confidence:.2f}"
                    logger.info(f"{message}")
                    if current_time - last_issue_reported_time >= 60:  # Limit to 1 message per minute.
                        send_notification(message)
                        last_issue_reported_time = current_time
                last_inference_time = current_time

            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Worker stopping.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        if cap is not None and cap.isOpened():
            cap.release()
        logger.info("Video stream released.")

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
        # Run directly the inference code
        terminate_event = multiprocessing.Event()
        _detect_issues_process(terminate_event)

        # Run for 60 seconds in a dedicated process
        # detector_process, terminate_event = start_issue_detector_process()
        # time.sleep(30) # Run for a fixed duration for testing this simplified model
    finally:
        # terminate_event.set() # Signal the worker to stop completely
        cv2.destroyAllWindows() # Close all OpenCV windows
