# tasks.py or celery.py
import os
from celery import Celery
from moviepy.editor import VideoFileClip
from api import logging


celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis broker URL
    backend="redis://localhost:6379/0",  # Redis result backend
)

celery_app.conf.update(
    include=["api.tasks"]  # Ensuring Celery knows where to look for tasks
)


@celery_app.task
def add(x, y):
    return x + y


@celery_app.task(bind=True)
def convert_video_to_audio(self, ref_id: str, files: list):
    request_output_dir = os.path.join("output", ref_id)
    os.makedirs(request_output_dir, exist_ok=True)

    processed_files = []

    for file in files:
        try:
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

        except Exception as e:
            logging.error(f"Error processing file {file['filename']}: {e}")
            raise self.retry(exc=e, countdown=30)  # Retry after 30 seconds

    return processed_files
