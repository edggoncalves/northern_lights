"""Logging utilities for Northern Lights."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "northern_lights",
    level: int = logging.INFO
) -> logging.Logger:
    """Set up and configure logger.

    Args:
        name: Logger name
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handler if not already configured
    if not logger.handlers:
        logger.setLevel(level)

        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Format: time - level - message
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get or create a logger.

    Args:
        name: Logger name (default: use root northern_lights logger)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"northern_lights.{name}")
    return logging.getLogger("northern_lights")
