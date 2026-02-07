import requests
import logging

def send_notification(config, message):
    """Sends a notification using the specified service."""
    service_url = config['notifier']['url']
    auth_token = config['notifier']['token']
    payload = {
        'event': 'printer_event',
        'message': {
            'text': message,
        }
    }
    push_url = f"{service_url}/push?auth_token={auth_token}"
    try:
        requests.post(push_url, json=payload)
        logging.info(f"Sent notification: {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send notification: {e}")
