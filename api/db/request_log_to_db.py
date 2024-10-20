from api.db.models import RequestLog
from sqlmodel import Session
from api.db import get_session  # Assuming you have a get_session dependency


async def write_request_log_to_db(log, db_session: Session):
    # Create a RequestLog instance from the log dict
    log_entry = RequestLog(
        url=log["URL"],
        method=log["METHOD"],
        process_time=log["PROCESS_TIME"],
        status_code=log["RESPONSE"],
    )

    db_session.add(log_entry)
    db_session.commit()
