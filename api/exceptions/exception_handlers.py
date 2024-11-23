from fastapi import HTTPException


# Custom exception
class AppException(HTTPException):
    def __init__(
        self, status_code: int = 500, detail: str | dict = {"INTERNAL SERVER ERROR"}
    ):
        super().__init__(status_code=status_code, detail=detail)


# Database exception
class DatabaseException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)
