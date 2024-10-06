import yaml


# Function to load YAML configuration
def load_db_config(file_path: str):
    with open(file_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            print(exc)
            return None
