import os
from celery import Celery
from moviepy.editor import VideoFileClip
from sqlalchemy.future import select
from api import logging
from api.models import TaskStatus
from datetime import datetime
from api.db import get_session, get_sync_session  # async and synchronous db sessions


celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis broker URL
    backend="redis://localhost:6379/0",  # Redis result backend
)

celery_app.conf.update(
    include=["api.tasks"]  # Ensuring Celery knows where to look for tasks
)


@celery_app.task(bind=True)
def convert_video_to_audio(self, ref_id: str, files: list):
    request_output_dir = os.path.join("output", ref_id)
    os.makedirs(request_output_dir, exist_ok=True)

    processed_files = []

    try:
        # synchronous session call
        with get_sync_session() as session:
            # Fetch the current task status
            task_status = session.execute(
                select(TaskStatus).filter(TaskStatus.ref_id == ref_id)
            ).scalar_one_or_none()

            if task_status:
                task_status.status = "IN_PROGRESS"
                task_status.updated_at = datetime.utcnow()
                session.add(task_status)
                session.commit()
            else:
                logging.error(f"Task status with ref_id {ref_id} not found.")
                return

            # Process the files
            for file in files:
                temp_file_path = os.path.join(request_output_dir, file["filename"])

                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(file["content"])

                video = VideoFileClip(temp_file_path)
                audio_file_path = os.path.join(
                    request_output_dir, f"{os.path.splitext(file['filename'])[0]}.mp3"
                )
                video.audio.write_audiofile(audio_file_path)
                video.close()

                processed_files.append(
                    {"video": file["filename"], "audio": audio_file_path}
                )

                # Cleanup: Delete the temporary video file
                os.remove(temp_file_path)

            # Update task status to "COMPLETED" after successful processing
            task_status = session.execute(
                select(TaskStatus).filter(TaskStatus.ref_id == ref_id)
            ).scalar_one_or_none()

            if task_status:
                task_status.status = "COMPLETED"
                task_status.result = str(processed_files)  # Store the result
                task_status.updated_at = datetime.utcnow()
                session.add(task_status)
                session.commit()  # Commit the final status update

        return processed_files

    except Exception as e:
        logging.error(f"Error processing files: {e}")

        # Update task status to "FAILED" in case of error
        with get_sync_session() as session:
            task_status = session.execute(
                select(TaskStatus).filter(TaskStatus.ref_id == ref_id)
            ).scalar_one_or_none()

            if task_status:
                task_status.status = "FAILED"
                task_status.result = f"Error: {str(e)}"  # Store the error message
                task_status.updated_at = datetime.utcnow()
                session.add(task_status)
                session.commit()

        raise self.retry(exc=e, countdown=30)  # Retry the task after 30 seconds
