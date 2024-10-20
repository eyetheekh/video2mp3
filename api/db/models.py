import uuid
from sqlmodel import SQLModel, Field
from datetime import datetime

# Define the User model
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(sa_column_kwargs={"unique": True})  # Add unique constraint
    key: str

# Define the RequestLog model
class RequestLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    url: str
    method: str
    process_time: float
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
