from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from api import logging
import time


class LoggingMiddleware(BaseHTTPMiddleware):
    # overriding the dispatch method in BaseHTTPMiddleware class
    async def dispatch(self, request: Request, call_next):
        # Log the time incoming request
        start = time.time()

        # Process the request and get the response
        response = await call_next(request)

        log_format_dict = {
            "URL": request.url.path,
            "METHOD": request.method,
            "PROCESS_TIME": time.time() - start,
            "RESPONSE": response.status_code,
        }

        # Log the request
        logging.info(f"Request: {log_format_dict}")
        return response
