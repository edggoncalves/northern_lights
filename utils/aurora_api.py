"""Client for Auroras.live API."""

import sys
from typing import Dict, Any

import requests

from utils.logger import get_logger

AURORAS_API = "http://api.auroras.live/v1/"

logger = get_logger("aurora_api")


def fetch_aurora_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch aurora visibility data from Auroras.live API.

    Args:
        latitude: Location latitude
        longitude: Location longitude

    Returns:
        Dictionary containing aurora data including KP index

    Raises:
        SystemExit: If API request fails
    """
    params = {
        "type": "all",
        "lat": latitude,
        "long": longitude,
        "forecast": "false",
        "threeday": "false",
    }
    try:
        logger.debug(
            f"Fetching aurora data for lat={latitude}, lon={longitude}"
        )
        response = requests.get(AURORAS_API, params=params, timeout=10)
        response.raise_for_status()
        logger.debug("Aurora data fetched successfully")
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Request to aurora API timed out")
        sys.exit("Error: Aurora API request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to aurora API")
        sys.exit(
            "Error: Could not connect to Aurora API. "
            "Check your internet connection."
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Aurora API request failed: {e}")
        sys.exit(f"Error: Failed to fetch aurora data: {e}")
