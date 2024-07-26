import logging
import os

from pathlib import Path

# Set up logging
log_dir = Path('/var/log/data_handler')
log_file = log_dir / 'data_handler.log'

# Create log directory if it does not exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up loggers
logger_names = ["data_consumer", "data_processor", "data_retriever"]
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
LOGGERS = []

for logger_name in logger_names:
    LOGGER = logging.getLogger(logger_name)
    LOGGER.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_dir / f"{logger_name}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    LOGGER.addHandler(file_handler)
    LOGGERS.append(LOGGER)
