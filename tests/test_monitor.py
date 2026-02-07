import unittest
from unittest.mock import patch, MagicMock
import yaml
import os
import requests

from src.monitor import main
from src.config import load_config
from src.printer import get_printer_status
from src.notifier import send_notification

class TestMonitor(unittest.TestCase):

    def setUp(self):
        """Set up a dummy config file for testing."""
        self.config_path = 'config/config.yaml'
        self.config = {
            'printer': {
                'ip': '127.0.0.1',
                'port': 7125,
                'api_key': 'test-api-key'
            },
            'notifier': {
                'url': 'http://test-server',
                'token': 'test-token'
            },
            'polling_interval_seconds': 0.1
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f)

    def tearDown(self):
        """Remove the dummy config file."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_load_config(self):
        """Test that the configuration is loaded correctly."""
        config = load_config(self.config_path)
        self.assertEqual(config, self.config)

    @patch('requests.get')
    def test_get_printer_status_printing(self, mock_get):
        """Test getting printer status when printing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'result': {
                'status': {
                    'print_stats': {
                        'state': 'printing'
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        status = get_printer_status(self.config)
        self.assertEqual(status, 'printing')

    @patch('requests.get')
    def test_get_printer_status_error(self, mock_get):
        """Test getting printer status when an error occurs."""
        mock_get.side_effect = requests.exceptions.RequestException
        status = get_printer_status(self.config)
        self.assertEqual(status, 'error')

    @patch('requests.post')
    def test_send_notification(self, mock_post):
        """Test sending a notification."""
        send_notification(self.config, "Test message")
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn('json', kwargs)
        self.assertEqual(kwargs['json']['event'], 'q1_event')
        self.assertEqual(kwargs['json']['message']['text'], 'Test message')

    @patch('src.monitor.get_printer_status')
    @patch('src.monitor.send_notification') # Patch the function in the module where it's used
    @patch('src.config.load_config') # Patch the function in its new module
    @patch('time.sleep', return_value=None)
    def test_main_loop_state_change(self, mock_sleep, mock_load_config, mock_send_notification, mock_get_printer_status):
        """Test the main loop detects a state change and sends a notification."""
        mock_load_config.return_value = self.config
        # Simulate the state change from printing to complete
        mock_get_printer_status.side_effect = ['printing', 'complete']

        main(max_iterations=1)

        mock_send_notification.assert_called_once_with(self.config, "Printer state changed from 'printing' to 'complete'.")

if __name__ == '__main__':
    unittest.main()
