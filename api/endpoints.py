from fastapi import APIRouter, Depends, Request
from fastapi.openapi.models import APIKey
from api.exceptions.exception_handlers import AppException, DatabaseException
from api.auth.validate_client import verify_api_key

# Router for the endpoints
endpoint_router = APIRouter(tags=["api"])


# POST /register with API key authentication and return the client's IP address
@endpoint_router.post("/register")
async def register(request: Request, api_key: APIKey = Depends(verify_api_key)):
    client_ip = request.client.host
    return {"message": "Hello World", "client_ip": client_ip}


# GET /login with API key authentication and return the client's IP address
@endpoint_router.get("/login")
async def login(request: Request, api_key: APIKey = Depends(verify_api_key)):
    client_ip = request.client.host
    return {"status": "ok", "client_ip": client_ip}


@endpoint_router.get("/example")
async def example_endpoint():
    raise AppException(detail={"error": "This is an application-level error."})


@endpoint_router.get("/db-error")
async def db_error_endpoint():
    raise DatabaseException(detail="Database connection failed.")
