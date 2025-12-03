import os
import sys

from loguru import logger

MINIMUM_LOG_LEVEL = "DEBUG"
LOG_DIR = "logs"

logger.remove()

if MINIMUM_LOG_LEVEL in ["DEBUG", "TRACE", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    minimum_log_level = MINIMUM_LOG_LEVEL
else:
    minimum_log_level = "DEBUG"

# Terminal output without tracebacks
logger.add(sys.stdout, level=minimum_log_level, backtrace=False, diagnose=False)


# Configuration of logging to a file
logger.add(
    os.path.join(LOG_DIR, "app.log"),
    rotation="500 MB",  # Rotate when file reaches 500 MB
    retention="10 days",  # Keep logs for 10 days
    compression="zip",  # Compress rotated logs
    level=minimum_log_level,
    backtrace=True,
    diagnose=True,
)

# Configuration of logging errors to a file
logger.add(
    os.path.join(LOG_DIR, "error.log"),
    rotation="100 MB",  # Rotate when file reaches 100 MB
    retention="30 days",  # Keep error logs longer
    compression="zip",
    level="ERROR",
    backtrace=True,
    diagnose=True,
)
