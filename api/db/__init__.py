from sqlmodel import Session, create_engine
from contextlib import asynccontextmanager
from api import logging, APP_DB_CONFIG


def get_database_url():
    """
    Returns the database URL based on the provided APP_DB_CONFIG.
    If APP_DB_CONFIG is not defined or does not contain a valid config,
    it defaults to SQLite.
    """
    config = APP_DB_CONFIG

    if not config:
        # Default to SQLite
        logging.info("No valid database config found, defaulting to SQLite.")
        return "sqlite:///./app_db.db"

    elif "mysql" in config:
        mysql_config = config["mysql"]
        return f"mysql+mysqlconnector://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database_name']}"

    elif "postgres" in config:
        postgres_config = config["postgres"]
        return f"postgresql+psycopg2://{postgres_config['user']}:{postgres_config['password']}@{postgres_config['host']}:{postgres_config['port']}/{postgres_config['database_name']}"


# Dependency to get a session for async functions
@asynccontextmanager
async def get_session():

    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL, echo=False)

    with Session(engine) as session:
        yield session
