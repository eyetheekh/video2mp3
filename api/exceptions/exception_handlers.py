from fastapi import HTTPException


# Custom exception
class AppException(HTTPException):
    def __init__(self, detail: str | dict):
        super().__init__(status_code=500, detail=detail)


# Database exception
class DatabaseException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)
