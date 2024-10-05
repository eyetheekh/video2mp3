import os
import mysql.connector
import logging
from api.config.load_config import load_db_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def make_or_test_db_connection():
    connection = None
    try:
        # Load the configuration from the YAML file
        config_path = os.path.join(os.path.dirname(__file__), "../config/configs.yml")
        print(f"Loading db configuration from: {config_path}")
        config = load_db_config(config_path)

        connection = mysql.connector.connect(
            host=config["mysql"]["host"],
            user=config["mysql"]["user"],
            password=config["mysql"]["password"],
            port=config["mysql"]["port"],
        )

        if connection.is_connected():
            logging.info("Successfully connected to the database.")
            db_name = config["mysql"]["database_name"]
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            db_exists = any(db[0] == db_name for db in databases)

            if not db_exists:
                cursor.execute(f"CREATE DATABASE {db_name}")
                logging.info("Database created: %s", db_name)
                return {"status": f"Database created: {db_name}"}
            else:
                logging.info("Database already exists: %s", db_name)
                return {
                    "connection": "success",
                    "message": "Database connection successful",
                    "info": f"Database already exists: {db_name}",
                }

    except mysql.connector.Error as err:
        logging.critical("Error: %s", str(err))
        return {
            "connection": "fail",
            "message": "Database connection unsuccessful",
            "info": {"error": str(err)},
        }

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("Database connection closed.")
