import logging
import os
from pathlib import Path

# Set up logging
log_dir = Path("/var/log/processors")
log_file = log_dir / "processors.log"

# Create log directory if it does not exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

LOGGER.addHandler(file_handler)
