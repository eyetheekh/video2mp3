from fastapi import APIRouter

endpoint_router = APIRouter(prefix="/api", tags=["api"])


@endpoint_router.get("/login")
def login():
    return {"status": "ok"}

