from loguru import logger
import os
import sys

# Determine the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the log file in the project's root directory
log_file_path = os.path.join(current_dir, "../../api.log")

# Ensure the path is resolved correctly
log_file_path = os.path.abspath(log_file_path)

# Print the log file path for debugging
print(f"Log file will be created at: {log_file_path}")

# Remove the default logger
logger.remove()

# Configure console logging with colors
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO",
)

# Configure file logging
logger.add(
    log_file_path,
    format="{time} - {level} - {message}",
    level="INFO",
    rotation="1 MB",  # Rotate log file when it reaches 1 MB
    compression="zip",  # Compress old log files
)

# Log an initial message to verify configuration
logger.info("Logger is configured and ready to use.")
