import os
import yaml
import logging
import shutil

def load_config(config_path='config/config.yaml'):
    """Loads the configuration from a YAML file."""
    if not os.path.exists(config_path):
        logging.error(f"Configuration file not found at {config_path}")
        # copy from example
        example_config_path = config_path + '.example'
        if os.path.exists(example_config_path):
            logging.info(f"Copying example configuration from {example_config_path}")
            shutil.copy(example_config_path, config_path)
        else:
            return None
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
