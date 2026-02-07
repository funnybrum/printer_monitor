import time
import logging

from .config import load_config
from .printer import get_printer_status
from .notifier import send_notification


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main(max_iterations=None):
    """Main function to run the printer monitor."""
    config = load_config()
    if not config:
        return

    polling_interval = config.get('polling_interval_seconds', 10)
    last_state = get_printer_status(config)

    logging.info("Starting Q1 Printer Monitor")

    iterations = 0
    while max_iterations is None or iterations < max_iterations:
        current_state = get_printer_status(config)

        if last_state == 'printing' and current_state != 'printing':
            message = f"Printer state changed from 'printing' to '{current_state}'."
            send_notification(config, message)

        last_state = current_state
        time.sleep(polling_interval)
        if max_iterations:
            iterations += 1


if __name__ == "__main__":
    main()
