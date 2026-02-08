import requests
import logging

def get_printer_status(config):
    """Gets the printer status from the Moonraker API."""
    printer_ip = config['printer']['ip']
    printer_port = config['printer']['port']
    url = f"http://{printer_ip}:{printer_port}/printer/objects/query?print_stats"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['result']['status']['print_stats']['state']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get printer status: {e}")
        return "error"
    except (KeyError, TypeError) as e:
        logging.error(f"Failed to parse printer status response: {e}")
        return "error"
