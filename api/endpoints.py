import os
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from fastapi.openapi.models import APIKey
from fastapi.responses import FileResponse
from sqlalchemy.future import select
from api.exceptions.exception_handlers import AppException, DatabaseException
from api.auth.validate_client import verify_api_key
from api import logging
from typing import Optional
from uuid import UUID, uuid4

# db session dependency
from sqlalchemy.ext.asyncio import AsyncSession
from api.db import get_session

# models
from api.models import TaskStatus


# celery,redis
from .tasks import celery_app, convert_video_to_audio


# Router for the endpoints
endpoint_router = APIRouter(tags=["api"], prefix="")


# Ensure directory for saving audio files
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@endpoint_router.post("/convert-task")
async def convert_task(
    request: Request,
    ref_id: Optional[UUID] = None,
    files: list[UploadFile] = File(...),
    api_key: APIKey = Depends(verify_api_key),
    db_session: AsyncSession = Depends(
        lambda: get_session(for_async_tasks=True)
    ),  # Pass parameter to Depends
):
    # Ensure ref_id is UUID, either from request or generate new
    ref_id = ref_id or str(uuid4())

    # Prepare file content
    file_list = [
        {"filename": file.filename, "content": await file.read()}
        for file in files
        if file.filename.endswith(".mp4")
    ]

    # Call Celery task asynchronously
    task = convert_video_to_audio.apply_async(args=[str(ref_id), file_list])

    # Store the task ID and ref_id in the database
    task_status = TaskStatus(ref_id=ref_id, task_id=task.id, status="PENDING")

    async with db_session as session:
        session.add(task_status)
        await session.commit()  # Commit changes asynchronously

    return {"message": "Conversion started", "ref_id": str(ref_id), "task_id": task.id}


@endpoint_router.get("/task-status/{ref_id}")
async def task_status(
    ref_id: str,
    db_session: AsyncSession = Depends(lambda: get_session(for_async_tasks=True)),
):
    logging.info(f"Status request for task {ref_id}")

    # Query the TaskStatus table by task_id
    async with db_session as session:
        task_status = await session.execute(
            select(TaskStatus).filter(TaskStatus.ref_id == ref_id)
        )
        task_status = task_status.scalar_one_or_none()

    # If the task doesn't exist, raise an HTTP exception
    if not task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return the status of the task
    return {
        "ref_id": task_status.ref_id,
        "task_id": task_status.task_id,
        "status": task_status.status,
    }


@endpoint_router.get("/convert/{ref_id}")
async def list_or_stream_files(
    ref_id: UUID,
    api_key: APIKey = Depends(verify_api_key),
):
    # Path for the requested `ref_id`
    ref_dir = os.path.join(OUTPUT_DIR, str(ref_id))

    # Check if the directory exists
    if not os.path.exists(ref_dir):
        raise AppException(status_code=404, detail="Reference ID not found")

    # List all MP3 files in the directory
    mp3_files = [f for f in os.listdir(ref_dir) if f.endswith(".mp3")]

    if not mp3_files:
        raise AppException(status_code=404, detail="No MP3 files found")

    # If only one file exists, stream it directly
    if len(mp3_files) == 1:
        file_path = os.path.join(ref_dir, mp3_files[0])
        return FileResponse(file_path, media_type="audio/mpeg", filename=mp3_files[0])

    # If multiple files exist, return a JSON list of downloadable URLs
    return {
        "ref_id": str(ref_id),
        "message": "Multiple files found. Use the download URLs to retrieve them.",
        "download_urls": [
            f"http://127.0.0.1:8000/convert/api/{ref_id}/download/{file_name}"
            for file_name in mp3_files
        ],
    }


@endpoint_router.get("/convert/{ref_id}/download/{file_name}")
async def download_file(
    ref_id: UUID,
    file_name: str,
    # api_key: APIKey = Depends(verify_api_key),
):
    # Path for the requested `ref_id`
    ref_dir = os.path.join(OUTPUT_DIR, str(ref_id))

    # Check if the directory exists
    if not os.path.exists(ref_dir):
        raise AppException(status_code=404, detail="Reference ID not found")

    # Path for the specific file
    file_path = os.path.join(ref_dir, file_name)

    # Check if the file exists
    if not os.path.exists(file_path) or not file_name.endswith(".mp3"):
        raise AppException(status_code=404, detail="File not found or invalid format")

    # Serve the file
    return FileResponse(file_path, media_type="audio/mpeg", filename=file_name)
