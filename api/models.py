from pydantic import BaseModel
from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime


class UserModel(BaseModel):
    username: str
    password: str


# Define the TaskStatus model
class TaskStatus(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ref_id: str  # Reference ID for tracking task relations (ref_id from user)
    task_id: str  # Task ID to link to specific tasks (task.id from celery)
    status: str  # Status of the task (e.g., 'PENDING', 'IN_PROGRESS', 'COMPLETED')
    result: str = Field(
        default=None, nullable=True
    )  # Result of the task, can be None initially
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Example of how the fields work:
# - id is the primary key and auto-generates a UUID.
# - ref_id and task_id can also be UUIDs representing references to ref_id got from user, task_id from celery's task.id
# - status will track the state of the task.
# - result will be filled in once the task is completed.
# - created_at and updated_at store timestamps for the task's lifecycle.
