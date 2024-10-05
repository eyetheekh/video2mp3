from fastapi import APIRouter
from api.db.make_or_test_db import make_or_test_db_connection

default_router = APIRouter()


@default_router.get("/ping", tags=["Root"])
async def ping():
    return {"data": "pong"}


@default_router.get("/test-db-connection", tags=["Root"])
async def test_db_connection():
    db_status = make_or_test_db_connection()
    return {"status": db_status}
