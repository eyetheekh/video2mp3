from fastapi import APIRouter
from pydantic import BaseModel

endpoint_router = APIRouter(prefix="/api", tags=["api"])


class UserModel(BaseModel):
    username: str
    password: str


@endpoint_router.post("/register")
def register(User: UserModel):

    return {"message": "Hello World"}


@endpoint_router.get("/login")
def login():
    return {"status": "ok"}

