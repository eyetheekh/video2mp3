import os
from .logging.logger import logger as logging
from api.config.load_config import load_db_config

# Load the configuration from the YAML file
config_path = os.path.join(os.path.dirname(__file__), "./config/configs.yml")
logging.info(f"Attempting to load DB configuration from: {config_path}")

try:
    APP_DB_CONFIG = load_db_config(config_path)
    logging.info(f"Successfully loaded DB configuration: {APP_DB_CONFIG}")
except Exception as e:
    logging.critical(f"Failed to load DB configuration: {e}")
