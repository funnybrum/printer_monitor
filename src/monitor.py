import time
import logging

from src.config import get_config
from src.printer import get_printer_status
from src.notifier import send_notification
from src.issue_detector import start_issue_detector_process

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

_issue_detector_process = None
_issue_detector_terminate_event = None

def terminate_issue_detector():
    global _issue_detector_process, _issue_detector_terminate_event
    if _issue_detector_process is not None:
        _issue_detector_terminate_event.set()  # Signal the worker to stop completely
        _issue_detector_process.join(timeout=5)  # Wait for worker to finish gracefully
        if _issue_detector_process.is_alive():
            logging.warning("Issue detector worker process did not terminate gracefully. Terminating forcefully.")
            _issue_detector_process.terminate()
        _issue_detector_process = None
        _issue_detector_terminate_event = None
        logging.info("Issue detector process shut down.")


def main():
    """Main function to run the printer monitor."""
    config = get_config()

    polling_interval = config['polling_interval_seconds']
    last_state = get_printer_status(config)

    logging.info("Starting Qidi Q1 Printer Monitor")

    try:
        while True:
            current_state = get_printer_status(config)

            global _issue_detector_process, _issue_detector_terminate_event
            if current_state == 'printing':
                if _issue_detector_process is None:
                    # Start issue detector process
                    logging.info("Printer is 'printing'. Starting issue detection process.")
                    _issue_detector_process, _issue_detector_terminate_event = start_issue_detector_process()
                else:
                    # Check if the issue detector process is alive
                    if not _issue_detector_process.is_alive():
                        logging.error("Issue detector process died unexpectedly.")
                        detector_process = None
            elif current_state != 'printing' and _issue_detector_process is not None:
                terminate_issue_detector()

            if last_state == 'printing' and current_state != 'printing':
                message = f"Printer state changed from 'printing' to '{current_state}'."
                send_notification(message)

            last_state = current_state
            time.sleep(polling_interval)
    finally:
        terminate_issue_detector()

if __name__ == "__main__":
    main()
