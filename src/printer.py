import requests
import logging

def get_printer_status(config):
    """Gets the printer status from the Moonraker API."""
    printer_ip = config['printer']['ip']
    printer_port = config['printer']['port']
    api_key = config['printer'].get('api_key')
    url = f"http://{printer_ip}:{printer_port}/printer/objects/query?print_stats"
    headers = {'X-Api-Key': api_key} if api_key else {}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['result']['status']['print_stats']['state']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get printer status: {e}")
        return "error"
    except (KeyError, TypeError) as e:
        logging.error(f"Failed to parse printer status response: {e}")
        return "error"
