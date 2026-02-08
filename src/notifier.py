import requests
import logging
from config import get_config

def send_notification(message):
    """Sends a notification using the specified service."""
    payload = {
        'event': 'printer_event',
        'message': {
            'text': message,
        }
    }
    service_url = get_config()['notifier']['url']
    auth_token = get_config()['notifier']['token']
    push_url = f"{service_url}/push?auth_token={auth_token}"
    try:
        requests.post(push_url, json=payload)
        logging.info(f"Sent notification: {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send notification: {e}")
