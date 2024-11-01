from fastapi import FastAPI, APIRouter, Depends, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.models import APIKey
from starlette.status import HTTP_403_FORBIDDEN
from api import API_KEYS

# Define the API Key name (the name of the header in which clients should send the key)
API_KEY_NAME = "x-api-key"


# Define the API key header dependency
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# Verify the API key
def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key in API_KEYS.values():
        return api_key
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
        )
