"""Client for Auroras.live API."""

import json
import sys
from typing import Dict, Any, Optional

import requests

from utils.logger import get_logger

AURORAS_API = "http://api.auroras.live/v1/"

logger = get_logger("aurora_api")


def fetch_aurora_data(
    latitude: float,
    longitude: float,
    save_output: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch aurora visibility data from Auroras.live API.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        save_output: Optional path to save raw API response

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
        data = response.json()

        # Save to file if requested
        if save_output:
            try:
                with open(save_output, "a") as f:
                    f.write(
                        f"# Response for lat={latitude}, lon={longitude}\n"
                    )
                    f.write(json.dumps(data, indent=2))
                    f.write("\n\n")
                logger.info(f"API response saved to {save_output}")
            except IOError as e:
                logger.error(f"Failed to save API response: {e}")
                print(f"Warning: Could not save API output to file: {e}")

        return data
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
