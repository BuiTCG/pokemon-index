import logging
import os

def setup_logger():
    """Configures a central logger that writes to both the terminal and a log file."""

    # 1. Define the logs directory at the root of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 2. Set the log file path
    log_file = os.path.join(log_dir, "pipeline.log")

    # 3. Create the logger
    logger = logging.getLogger("PokemonIndex")
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if logger is imported multiple times
    if not logger.handlers:
        # 4. Format: [Timestamp] - [LEVEL] - [Message]
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # Handler 1: Write to the .log file
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Handler 2: Still print to the terminal (useful for when you are testing in Dev)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

# Create the globally accessible logger instance
logger = setup_logger()