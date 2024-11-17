from fastapi import Request
from api.db.models import RequestLog
from sqlmodel import Session
from api.db import get_session


async def write_request_log_to_db(log, db_session: Session, request: Request):
    # Create a RequestLog instance from the log dict
    log_entry = RequestLog(
        url=log["URL"],
        method=log["METHOD"],
        request_body_type=request.headers.get("content-type", ""),
        process_time=log["PROCESS_TIME"],
        status_code=log["RESPONSE"],
        client_ip=request.client.host,
        api_key=request.headers.get("x-api-key", ""),
        user_agent=request.headers.get("user-agent", ""),
    )
    # Use 'async with' to properly manage the session
    async with get_session(for_async_tasks=True) as db_session:
        db_session.add(log_entry)
        await db_session.commit()
