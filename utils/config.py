"""Configuration management for Northern Lights."""

import json
import os
import re
import sys
from typing import Dict, Any, List

from utils.geocoding import get_coordinates

CONFIGURATION = "config.json"


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate configuration structure and contents.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check notification threshold
    if "notification_threshold" in config:
        threshold = config["notification_threshold"]
        valid_thresholds = ["HIGH", "MODERATE", "ALL"]
        if threshold not in valid_thresholds:
            errors.append(
                f"notification_threshold must be one of: "
                f"{', '.join(valid_thresholds)}"
            )

    # Check for locations (new format) or city/country (old format)
    if "locations" in config:
        if not isinstance(config["locations"], list):
            errors.append("'locations' must be a list")
        elif len(config["locations"]) == 0:
            errors.append("At least one location must be configured")
        else:
            for i, loc in enumerate(config["locations"]):
                if not isinstance(loc, dict):
                    errors.append(f"Location {i+1} must be a dictionary")
                    continue
                required_keys = ["city", "country", "latitude", "longitude"]
                missing = [k for k in required_keys if k not in loc]
                if missing:
                    errors.append(
                        f"Location {i+1} missing keys: {', '.join(missing)}"
                    )
                # Validate coordinates
                if "latitude" in loc:
                    try:
                        lat = float(loc["latitude"])
                        if not -90 <= lat <= 90:
                            errors.append(
                                f"Location {i+1} latitude must be "
                                f"between -90 and 90"
                            )
                    except (ValueError, TypeError):
                        errors.append(
                            f"Location {i+1} latitude must be a number"
                        )
                if "longitude" in loc:
                    try:
                        lng = float(loc["longitude"])
                        if not -180 <= lng <= 180:
                            errors.append(
                                f"Location {i+1} longitude must be "
                                f"between -180 and 180"
                            )
                    except (ValueError, TypeError):
                        errors.append(
                            f"Location {i+1} longitude must be a number"
                        )
    elif "city" in config and "country" in config:
        # Old format - check for required coordinate fields
        if "latitude" not in config or "longitude" not in config:
            errors.append(
                "Old format config missing latitude or longitude"
            )
    else:
        errors.append(
            "Config must have either 'locations' or 'city'/'country'"
        )

    # Check for emails (new format) or email (old format)
    if "emails" in config:
        if not isinstance(config["emails"], list):
            errors.append("'emails' must be a list")
        elif len(config["emails"]) == 0:
            errors.append("At least one email must be configured")
        else:
            for email in config["emails"]:
                if not validate_email(email):
                    errors.append(f"Invalid email format: {email}")
    elif "email" in config:
        if not validate_email(config["email"]):
            errors.append(f"Invalid email format: {config['email']}")
    else:
        errors.append("Config must have either 'emails' or 'email'")

    return errors


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file.

    Returns:
        Dictionary containing configuration data

    Raises:
        SystemExit: If config file not found or is invalid
    """
    config_location = os.path.join(os.getcwd(), CONFIGURATION)
    if not os.path.exists(config_location):
        sys.exit(
            "Configuration file not found. "
            "Please run 'python main.py configure' to create one."
        )
    try:
        with open(config_location, "r") as f:
            config = json.load(f)

        # Validate configuration
        errors = validate_config(config)
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(
                "\nPlease run 'python main.py configure' to fix "
                "the configuration."
            )

        return config
    except json.JSONDecodeError:
        sys.exit(
            "Error: Configuration file is corrupted. "
            "Please run 'python main.py configure' to recreate it."
        )


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to config.json file.

    Args:
        config: Dictionary containing configuration data
    """
    config_location = os.path.join(os.getcwd(), CONFIGURATION)
    with open(config_location, "w") as f:
        json.dump(config, f, indent=2)


def config_exists() -> bool:
    """Check if configuration file exists.

    Checks for the presence of config.json in the current
    working directory.

    Returns:
        True if config file exists, False otherwise
    """
    config_location = os.path.join(os.getcwd(), CONFIGURATION)
    return os.path.exists(config_location)


def display_config_summary(config: Dict[str, Any]) -> None:
    """Display current configuration summary.

    Shows a brief summary of the current configuration including
    location and email addresses (with sensitive data hidden).

    Args:
        config: Configuration dictionary
    """
    print("Configuration file found:")
    try:
        # Display current settings (hide sensitive data)
        display_config = config.copy()
        if "emails" in display_config:
            location_str = (
                f"  Location: {config.get('city', 'N/A')}, "
                f"{config.get('country', 'N/A')}"
            )
            print(location_str)
            print(f"  Emails: {', '.join(config['emails'])}")
        elif "email" in display_config:
            print(
                f"  Location: {config.get('city', 'N/A')}, "
                f"{config.get('country', 'N/A')}"
            )
            print(f"  Email: {config['email']}")
    except (KeyError, TypeError):
        print("(Corrupted configuration file - will create new)")


def manage_locations(config: Dict[str, Any]) -> None:
    """Interactive location management interface.

    Provides a menu-driven interface to add or remove locations.
    Automatically geocodes city/country pairs to get coordinates.
    Converts old single-location format to new multi-location format.
    Saves changes to config.json.

    Args:
        config: Configuration dictionary to modify
    """
    # Convert old single location format to new locations list
    if "city" in config and "locations" not in config:
        config["locations"] = [
            {
                "city": config.pop("city"),
                "country": config.pop("country"),
                "latitude": config.pop("latitude"),
                "longitude": config.pop("longitude"),
            }
        ]

    locations = config.get("locations", [])

    while True:
        print("\n--- Location Management ---")
        if locations:
            for i, loc in enumerate(locations, 1):
                print(
                    f"  {i}. {loc['city']}, {loc['country']} "
                    f"({loc['latitude']:.4f}, {loc['longitude']:.4f})"
                )
        else:
            print("  (no locations configured)")

        print("\nOptions:")
        print("  a. Add new location")
        if locations:
            print("  r. Remove location")
        print("  d. Done (save and exit)")
        location_choice = input("\nChoice: ").strip().lower()

        if location_choice == "a":
            print("\nEnter new location details:")
            city = input("City: ")
            country = input("Country: ")
            print("\nLooking up coordinates...")
            lat, lng = get_coordinates(city, country)
            locations.append(
                {
                    "city": city,
                    "country": country,
                    "latitude": lat,
                    "longitude": lng,
                }
            )
            print(f"Added: {city}, {country} ({lat:.4f}, {lng:.4f})")

        elif location_choice == "r" and locations:
            try:
                idx = int(input("Enter location number to remove: ")) - 1
                if 0 <= idx < len(locations):
                    removed = locations.pop(idx)
                    print(f"Removed: {removed['city']}, {removed['country']}")
                else:
                    print("Invalid location number.")
            except ValueError:
                print("Invalid input.")

        elif location_choice == "d":
            if locations:
                config["locations"] = locations
                save_config(config)
                print(f"\nLocations saved ({len(locations)} location(s)).")
            else:
                print(
                    "Warning: No locations configured. "
                    "Add at least one location."
                )
                continue
            break

        else:
            print("Invalid choice.")


def manage_emails(config: Dict[str, Any]) -> None:
    """Interactive email recipient management.

    Prompts for comma-separated email addresses, validates them,
    and saves to configuration. Removes old single 'email' field
    if present. Saves changes to config.json.

    Args:
        config: Configuration dictionary to modify
    """
    print("\nCurrent recipients:")
    emails = config.get(
        "emails", [config.get("email")] if config.get("email") else []
    )
    if emails:
        for i, email in enumerate(emails, 1):
            print(f"  {i}. {email}")
    else:
        print("  (none configured)")

    email_input = input(
        "\nEnter email(s) for notifications (comma-separated for multiple): "
    )
    emails = [email.strip() for email in email_input.split(",")]

    # Validate all email addresses
    invalid_emails = [email for email in emails if not validate_email(email)]
    if invalid_emails:
        print(
            f"\nError: Invalid email address(es): "
            f"{', '.join(invalid_emails)}"
        )
        print("Please check the format and try again.")
        return

    config["emails"] = emails
    # Remove old 'email' field if it exists
    config.pop("email", None)
    save_config(config)
    print(f"\nEmail recipients updated: {', '.join(emails)}")


def manage_notification_threshold(config: Dict[str, Any]) -> None:
    """Interactive notification threshold management.

    Args:
        config: Configuration dictionary to modify
    """
    current = config.get("notification_threshold", "HIGH")

    print("\n=== Notification Threshold ===")
    print(f"Current setting: {current}")
    print("\nAvailable options:")
    print("  1. HIGH - Only KP index >= 5 (best viewing conditions)")
    print("  2. MODERATE - KP index >= 3 (good viewing conditions)")
    print("  3. ALL - Any aurora activity detected (KP > 0)")
    print()

    choice = input(
        "Select threshold (1-3) or press Enter to keep current: "
    ).strip()

    if choice == "1":
        config["notification_threshold"] = "HIGH"
        print("\nNotification threshold set to HIGH (KP >= 5)")
    elif choice == "2":
        config["notification_threshold"] = "MODERATE"
        print("\nNotification threshold set to MODERATE (KP >= 3)")
    elif choice == "3":
        config["notification_threshold"] = "ALL"
        print("\nNotification threshold set to ALL (KP > 0)")
    elif choice == "":
        print(f"\nKeeping current threshold: {current}")
        return
    else:
        print("\nInvalid choice. Keeping current threshold.")
        return

    save_config(config)
    print("Configuration saved!")


def configure_smtp() -> None:
    """Configure SMTP settings and save to .env file.

    Prompts for SMTP server, port, username, and password.
    Creates or overwrites .env file in the current directory
    with the provided credentials. The .env file is gitignored
    to protect sensitive credentials.
    """
    print("\nEnter your SMTP email settings:")
    smtp_server = input("SMTP Server (e.g., smtp.gmail.com): ")
    smtp_port = input("SMTP Port (default 587): ") or "587"
    smtp_username = input("SMTP Username: ")
    smtp_password = input("SMTP Password (or app-specific password): ")

    # Create/update .env file
    env_path = os.path.join(os.getcwd(), ".env")
    with open(env_path, "w") as f:
        f.write(f"SMTP_SERVER={smtp_server}\n")
        f.write(f"SMTP_PORT={smtp_port}\n")
        f.write(f"SMTP_USERNAME={smtp_username}\n")
        f.write(f"SMTP_PASSWORD={smtp_password}\n")

    print("\nSMTP settings saved to .env file!")
    print("Note: .env file contains sensitive credentials and is gitignored.")
    print("\nTo test your email configuration, run:")
    print("  uv run python main.py test-email")


def setup_complete_config() -> Dict[str, Any]:
    """Complete configuration setup for new installations.

    Guides the user through setting up:
    - One or more monitoring locations (with geocoding)
    - One or more email notification recipients (with validation)
    - Optional SMTP email server settings

    Saves the configuration to config.json.

    Returns:
        Complete configuration dictionary
    """
    config = {"locations": []}

    # Get locations
    print("\nLet's add your monitoring locations.")
    while True:
        print(f"\nLocation #{len(config['locations']) + 1}:")
        city = input("Enter city: ")
        country = input("Enter country: ")
        print("\nLooking up coordinates...")
        lat, lng = get_coordinates(city, country)
        config["locations"].append(
            {
                "city": city,
                "country": country,
                "latitude": lat,
                "longitude": lng,
            }
        )
        print(f"Added: {city}, {country} ({lat:.4f}, {lng:.4f})")

        if input("\nAdd another location? (Y/N): ").strip().lower() != "y":
            break

    # Get email addresses (supports multiple)
    while True:
        email_input = input(
            "\nEnter email(s) for notifications "
            "(comma-separated for multiple): "
        )
        emails = [email.strip() for email in email_input.split(",")]

        # Validate all email addresses
        invalid_emails = [
            email for email in emails if not validate_email(email)
        ]
        if invalid_emails:
            print(
                f"Error: Invalid email address(es): "
                f"{', '.join(invalid_emails)}"
            )
            print("Please check the format and try again.")
            continue
        break

    config["emails"] = emails

    # Set notification threshold
    print("\n=== Notification Threshold ===")
    print("When should you receive alerts?")
    print("  1. HIGH - Only KP >= 5 (best viewing, less frequent)")
    print("  2. MODERATE - KP >= 3 (good viewing, more frequent)")
    print("  3. ALL - Any activity (KP > 0, most frequent)")
    print()
    threshold_choice = input("Select (1-3, default is HIGH): ").strip()

    if threshold_choice == "2":
        config["notification_threshold"] = "MODERATE"
    elif threshold_choice == "3":
        config["notification_threshold"] = "ALL"
    else:
        config["notification_threshold"] = "HIGH"

    save_config(config)

    print("\nConfiguration saved successfully!")
    print(f"Locations: {len(config['locations'])}")
    for loc in config["locations"]:
        print(
            f"  - {loc['city']}, {loc['country']} "
            f"({loc['latitude']:.4f}, {loc['longitude']:.4f})"
        )
    print(f"Email recipients: {', '.join(emails)}")

    # Ask if user wants to configure email settings
    print("\nWould you like to configure SMTP email settings now?")
    email_response = input("Y/N: ")

    if email_response.lower() == "y":
        configure_smtp()
    else:
        print("\nTo configure SMTP later, run:")
        print("  uv run python main.py configure")
        print("  and select option 3 (SMTP settings)")

    return config
