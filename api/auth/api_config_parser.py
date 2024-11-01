import yaml


# Function to load API keys from YAML configuration
def load_api_keys(file_path: str):
    with open(file_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            # Extract API keys from the 'API-KEYS' section
            api_keys = config.get("API-KEYS", {})
            return {
                "dev": api_keys.get("dev"),
                "test": api_keys.get("test"),
                "prod": api_keys.get("prod"),
            }
        except yaml.YAMLError as exc:
            print(exc)
            raise RuntimeWarning("Failed to load API keys from the configuration file.")
