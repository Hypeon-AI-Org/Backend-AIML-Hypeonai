from loguru import logger
import sys
from app.core.config import settings

# Remove default logger
logger.remove()

# Add stdout logger with INFO level
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    colorize=True
)

# Add file logger with rotation
logger.add(
    "logs/app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    rotation="500 MB",
    retention="10 days",
    compression="zip"
)

# Export logger
__all__ = ["logger"]