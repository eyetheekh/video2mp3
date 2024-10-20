import uuid
from sqlmodel import SQLModel, Field, create_engine, Session
from api import APP_DB_CONFIG, logging
from api.db.models import User  # Ensure User is imported
from api.db import get_database_url


def make_or_test_db_connection():
    """
    Test the database connection and create the database if necessary.
    """

    def create_db_and_tables():
        """
        Create the database and tables if they do not exist.
        Ensure that user the model is imported in the same module to be registered in the sqlmodel metadata.
        """
        SQLModel.metadata.create_all(engine)

    try:
        # Create the database engine
        database_url = get_database_url()
        engine = create_engine(database_url, echo=True)  # Ensure engine is created

        # Test the connection and create tables
        with Session(engine) as session:
            logging.info("Successfully connected to the database.")

            # Create the database tables (if not already present)
            create_db_and_tables()
            logging.success("Database tables created successfully.")

            return {
                "connection": "success",
                "message": "Database connection successful",
                "info": "Database is ready with table User",
            }

    except Exception as err:
        logging.critical(str(err))
        return {
            "connection": "fail",
            "message": "Database connection unsuccessful",
            "info": {"error": str(err)},
        }
