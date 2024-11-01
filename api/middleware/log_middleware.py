from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from api import logging
import time
from api.db import get_session
from api.db.request_log_to_db import write_request_log_to_db


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
            "PROCESS_TIME": round(time.time() - start, 3),
            "RESPONSE": response.status_code,
        }

        # Use 'async with' to properly manage the session
        async with get_session() as db_session:
            await write_request_log_to_db(
                log=log_format_dict, db_session=db_session, request=request
            )

        # Log the request
        logging.info(f"Request: {log_format_dict}")
        return response
