import os
from fastapi import APIRouter, Depends, Request, File, UploadFile
from fastapi.openapi.models import APIKey
from fastapi.responses import FileResponse
from sqlmodel import Session
from api.exceptions.exception_handlers import AppException, DatabaseException
from api.auth.validate_client import verify_api_key
from api import logging
from typing import Optional
from uuid import UUID, uuid4

# db session dependency
from sqlalchemy.ext.asyncio import AsyncSession
from api.db import get_session

# convertions
from moviepy.editor import VideoFileClip

# celery,redis
# Ensure correct import of the Celery instance
from celery.result import AsyncResult

from api.models import TaskStatus
from .tasks import celery_app, add, convert_video_to_audio


# Router for the endpoints
endpoint_router = APIRouter(tags=["api"], prefix="")


# POST /register with API key authentication and return the client's IP address
# @endpoint_router.post("/register")
async def register(request: Request, api_key: APIKey = Depends(verify_api_key)):
    logging.info(f"Register endpoint called from IP: {request.client.host}")
    client_ip = request.client.host
    return {"message": "Hello World", "client_ip": client_ip}


# GET /login with API key authentication and return the client's IP address
# @endpoint_router.get("/login")
async def login(request: Request, api_key: APIKey = Depends(verify_api_key)):
    logging.info(f"Login endpoint called from IP: {request.client.host}")
    client_ip = request.client.host
    return {"status": "ok", "client_ip": client_ip}


# @endpoint_router.get("/example")
async def example_endpoint():
    logging.error("Application error occurred in example endpoint")
    raise AppException(detail={"error": "This is an application-level error."})


# @endpoint_router.get("/db-error")
async def db_error_endpoint():
    logging.error("Database error occurred in db-error endpoint")
    raise DatabaseException(detail="Database connection failed.")


# Ensure directory for saving audio files
OUTPUT_DIR = "audio_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# @endpoint_router.post("/convert")
async def convert(
    request: Request,
    ref_id: Optional[UUID] = None,
    files: list[UploadFile] = File(...),
    api_key: APIKey = Depends(verify_api_key),
):
    logging.info(f"Convert endpoint called from IP: {request.client.host}")

    if not files:
        raise AppException(status_code=400, detail="No files provided")

    # Validate file types
    invalid_files = [
        file.filename for file in files if not file.filename.endswith(".mp4")
    ]
    if invalid_files:
        raise AppException(
            status_code=400,
            detail=f"Only MP4 files are allowed. Invalid files: {invalid_files}",
        )

    # Use provided ref_id or generate a new UUID
    ref_id = ref_id or uuid4()

    # Create a unique output directory for the request
    request_output_dir = os.path.join(OUTPUT_DIR, str(ref_id))
    os.makedirs(request_output_dir, exist_ok=True)

    processed_files = []

    for file in files:
        try:
            # Save the uploaded file temporarily
            temp_file_path = os.path.join(request_output_dir, file.filename)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(await file.read())

            # Convert video to audio
            video = VideoFileClip(temp_file_path)
            audio_file_path = os.path.join(
                request_output_dir, f"{os.path.splitext(file.filename)[0]}.mp3"
            )
            video.audio.write_audiofile(audio_file_path)
            video.close()

            processed_files.append({"video": file.filename, "audio": audio_file_path})

            # Cleanup: Delete the temporary video file
            os.remove(temp_file_path)

        except Exception as e:
            logging.error(f"Error processing file {file.filename}: {e}")
            raise AppException(
                status_code=500,
                detail=f"Error processing file {file.filename}: {str(e)}",
            )

    return {
        "message": f"Processed {len(processed_files)} file(s)",
        "ref_id": str(ref_id),
        "files": processed_files,
    }


# @endpoint_router.get("/convert/{ref_id}")
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


# @endpoint_router.post("/add")
def add_numbers(a: int, b: int):
    task = add.delay(a, b)  # Send task to Celery
    return {"task_id": task.id, "status": "Task submitted"}


# @endpoint_router.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(
        task_id, app=celery_app
    )  # Use the Celery app to initialize AsyncResult
    if result.state == "SUCCESS":
        return {"status": result.state, "result": result.result}
    return {"status": result.state, "result": None}


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
    logging.info("Convert endpoint called from IP")

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
