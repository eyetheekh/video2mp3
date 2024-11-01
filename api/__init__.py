import os
from .logging.logger import logger as logging
from api.config.load_config import load_db_config
from api.auth.api_config_parser import load_api_keys


try:
    # Load the db configuration from the YAML file
    db_config_path = os.path.join(os.path.dirname(__file__), "./config/configs.yml")
    logging.info(f"Attempting to load DB configuration from: {db_config_path}")
    APP_DB_CONFIG = load_db_config(db_config_path)
    logging.info(f"Successfully loaded DB configuration: {APP_DB_CONFIG}")

    # Load the APIKEYS configuration from the YAML file
    apikey_config_path = os.path.join(os.path.dirname(__file__), "./auth/auth.yml")
    logging.info(f"Attempting to load DB configuration from: {apikey_config_path}")
    API_KEYS = load_api_keys(apikey_config_path)
    logging.info(f"Successfully loaded APIKEYS configuration:")

except Exception as e:
    logging.critical(f"Failed to load configuration: {e}")
    raise RuntimeError("Failed to load configuration.")
