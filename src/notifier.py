import logging
import requests
import uuid

from src.config import get_config


def send_notification(message, image=None, event_type='printer_event'):
    service_url = get_config()['notifier']['url']
    auth_token = get_config()['notifier']['token']

    payload = {
        'event': event_type,
        'message': {
            'text': message,
        }
    }

    if image:
        image_name = "%s.jpg" % str(uuid.uuid4())
        upload_url = "%s/image?auth_token=%s" % (service_url, auth_token)
        requests.put(upload_url, files={image_name: image})

        payload['message']['image'] = image_name
        payload['message']['thumbnail'] = image_name

    push_url = "%s/push?auth_token=%s" % (service_url, auth_token)
    try:
        requests.post(push_url, json=payload)
    except requests.exceptions.RequestException as e:
        logging.exception(f"Failed to send notification {payload}.")