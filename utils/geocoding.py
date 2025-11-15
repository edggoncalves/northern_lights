"""Geocoding utilities for converting locations to coordinates."""

import sys
from typing import Tuple

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from utils.logger import get_logger

logger = get_logger("geocoding")


def get_coordinates(city: str, country: str) -> Tuple[float, float]:
    """Get latitude and longitude for a given city and country.

    Args:
        city: City name
        country: Country name

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        SystemExit: If geocoding fails
    """
    try:
        logger.debug(f"Looking up coordinates for {city}, {country}")
        geolocator = Nominatim(user_agent="northern-lights-tracker")
        location = geolocator.geocode(f"{city}, {country}", timeout=10)
        if location is None:
            logger.error(f"Location not found: {city}, {country}")
            sys.exit(
                f"Error: Could not find location for '{city}, {country}'. "
                "Please check the spelling."
            )
        logger.info(
            f"Found coordinates for {city}, {country}: "
            f"{location.latitude}, {location.longitude}"
        )
        return location.latitude, location.longitude
    except GeocoderTimedOut:
        logger.error("Geocoding service timed out")
        sys.exit("Error: Geocoding service timed out. Please try again.")
    except GeocoderServiceError as e:
        logger.error(f"Geocoding service error: {e}")
        sys.exit(f"Error: Geocoding service failed: {e}")
