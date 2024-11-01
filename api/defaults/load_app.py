from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from api.db.make_or_test_db import make_or_test_db_connection
from api.exceptions.exception_handlers import AppException, DatabaseException
from .router import default_router
from api import logging
from api.middleware.log_middleware import LoggingMiddleware


class FastAPIApp:
    def __init__(self):
        logging.info("Initializing FastAPI app...")

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
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        )

        # Configure CORS
        self.configure_cors()

        # Include routers
        self.include_routers()

        # Adding Logging Middleware to the app
        logging.info("Adding LoggingMiddleware to the app...")
        self.app.add_middleware(LoggingMiddleware)

        # Connect to the database
        db_connection_result = self.connect_to_db()
        if db_connection_result:
            logging.info(f"Database status: {db_connection_result}")

        # Register exception handlers
        self.register_exception_handlers()

        logging.info("FastAPI app initialized successfully.")

    def connect_to_db(self) -> str:
        """Connect to the database and return the status."""
        try:
            connection_info = make_or_test_db_connection()
            if connection_info["connection"] == "success":
                logging.success(f"Database connection successful: {connection_info}")
            else:
                logging.critical(f"Database connection failed: {connection_info}")
            return connection_info.get(
                "message", "Database connection check completed."
            )
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            return "Failed to connect to the database."

    def configure_cors(self) -> None:
        """Configure CORS settings for the application."""
        origins = ["*"]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logging.info(f"CORS configured with allowed origins: {origins}")

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
            logging.critical(f"Could not import endpoints router: {e}")
        except Exception as e:
            logging.error(
                f"An error occurred while including the endpoints router: {e}"
            )

    def register_exception_handlers(self):
        """Register custom exception handlers."""

        @self.app.exception_handler(AppException)
        async def app_exception_handler(request: Request, exc: AppException):
            raise HTTPException(status_code=exc.status_code, detail=exc.detail)

        @self.app.exception_handler(DatabaseException)
        async def database_exception_handler(request: Request, exc: DatabaseException):
            raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    def return_app(self) -> FastAPI:
        """Return the FastAPI app instance."""
        return self.app


def load_app() -> FastAPI:
    """Load the FastAPI application."""
    return FastAPIApp().return_app()
