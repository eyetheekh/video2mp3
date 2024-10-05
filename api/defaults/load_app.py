from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.db.make_or_test_db import make_or_test_db_connection
from .router import default_router
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class FastAPIApp:
    def __init__(self):
        self.app = FastAPI(
            title="Video2MP3",
            description="This is a FastAPI Microservice",
            contact={
                "name": "Aythikh",
                "email": "www.aytheeh@gmail.com",
            },
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
        )
        self.configure_cors()
        self.include_routers()

        db_connection_result = self.connect_to_db()
        if db_connection_result:
            logging.info(db_connection_result)

        logging.info("FastAPI app initialized")

    def connect_to_db(self) -> str:
        """Connect to the database and return the status."""
        try:
            connection_info = make_or_test_db_connection()
            logging.critical("Database connection check: %s", connection_info)
            return connection_info.get(
                "message", "Database connection check completed."
            )
        except Exception as e:
            logging.error("Error connecting to the database: %s", e)
            return "Failed to connect to the database."

    def configure_cors(self) -> None:
        """Configure CORS settings for the application."""
        origins = [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:4000",
            "http://localhost:19006",
        ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logging.info("CORS configured with origins: %s", origins)

    def include_routers(self) -> None:
        """Include routers in the FastAPI application."""
        self.app.include_router(default_router, prefix="/root")
        logging.info("Included default router with prefix '/root'")

        try:
            from api.endpoints import endpoint_router

            if endpoint_router:
                self.app.include_router(endpoint_router, prefix="/endpoints")
                logging.info("Included endpoints router with prefix '/endpoints'")
        except ImportError as e:
            logging.error("Could not import endpoints router: %s", e)
        except Exception as e:
            logging.error(
                "An error occurred while including the endpoints router: %s", e
            )

    def return_app(self) -> FastAPI:
        """Return the FastAPI app instance."""
        return self.app


def load_app() -> FastAPI:
    """Load the FastAPI application."""
    return FastAPIApp().return_app()
