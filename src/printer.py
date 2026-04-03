import requests
import logging

_printer_offline = False

def get_printer_status(config):
    """Gets the printer status from the Moonraker API."""
    global _printer_offline
    printer_ip = config['printer']['ip']
    printer_port = config['printer']['port']
    url = f"http://{printer_ip}:{printer_port}/printer/objects/query?print_stats"
    try:
        response = requests.get(url)
        response.raise_for_status()
        state = response.json()['result']['status']['print_stats']['state']
        if _printer_offline:
            logging.info("Printer is back online.")
            _printer_offline = False
        return state
    except requests.exceptions.RequestException as e:
        if not _printer_offline:
            logging.error(f"Failed to get printer status: {e}")
            logging.info("Printer appears to be offline. Suppressing further connection errors.")
            _printer_offline = True
        return "error"
    except (KeyError, TypeError) as e:
        logging.error(f"Failed to parse printer status response: {e}")
        return "error"
