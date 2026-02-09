import os
import yaml
import logging

_config = None

def _load_config_from_file(config_path='config/config.yaml'):
    if not os.path.exists(config_path):
        raise RuntimeError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_config():
    """
    Returns the cached configuration, loading it if not already loaded.
    This implements a lazy-loading singleton pattern for the configuration.
    """
    global _config
    if _config is None:
        try:
            _config = _load_config_from_file()
        except:
            logging.exception("Failed to load configuration")
            raise
    return _config
