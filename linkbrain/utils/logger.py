"""
Logging utilities for LinkBrain.
"""

import logging
import sys
from typing import Optional

__all__ = ['setup_logging', 'get_logger']


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> None:
    """
    Setup logging configuration for LinkBrain.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string (optional)
        include_timestamp: Include timestamp in log messages
    
    Example:
        >>> from linkbrain.utils.logger import setup_logging
        >>> setup_logging(level=logging.DEBUG)
    """
    if format_string is None:
        if include_timestamp:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger instance with optional level override.
    
    Args:
        name: Logger name (typically __name__)
        level: Optional logging level override
    
    Returns:
        Logger instance
    
    Example:
        >>> from linkbrain.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Device initialized")
    """
    logger = logging.getLogger(name)
    
    if level is not None:
        logger.setLevel(level)
    
    return logger