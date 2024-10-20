from fastapi import APIRouter
from api.models import UserModel

endpoint_router = APIRouter(tags=["api"])


@endpoint_router.post("/register")
def register(User: UserModel):

    return {"message": "Hello World"}


@endpoint_router.get("/login")
def login():
    return {"status": "ok"}

