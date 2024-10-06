import uuid
from sqlmodel import SQLModel, Field


# Define the User model
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(sa_column_kwargs={"unique": True})  # Add unique constraint
    key: str
