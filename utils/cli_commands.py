"""CLI command implementations for Northern Lights."""

import os
from typing import Dict, Any, List, Tuple

from utils.config import (
    load_config,
    config_exists,
    display_config_summary,
    manage_locations,
    manage_emails,
    manage_notification_threshold,
    configure_smtp,
    setup_complete_config,
)
from utils.aurora_api import fetch_aurora_data
from utils.email_notifier import send_email
from utils.email_formatter import (
    create_aurora_alert_email,
    create_test_email
)


def configure() -> None:
    """Interactive configuration setup.

    Stores user location and email settings.
    """
    # Check if config exists and load it
    config = {}
    if config_exists():
        display_config_summary(load_config())
        config = load_config()

        print("\nWhat would you like to configure?")
        print("  1. Locations (city and country)")
        print("  2. Email recipients")
        print("  3. Notification threshold (HIGH/MODERATE/ALL)")
        print("  4. SMTP settings (email server)")
        print("  5. All settings (complete reconfiguration)")
        print("  6. Exit")
        choice = input("\nEnter your choice (1-6): ").strip()
    else:
        print("No configuration file found. Let's create one!")
        choice = "5"

    if choice == "1":
        # Manage locations
        manage_locations(config)

    elif choice == "2":
        # Update email recipients only
        manage_emails(config)

    elif choice == "3":
        # Update notification threshold
        manage_notification_threshold(config)

    elif choice == "4":
        # Update SMTP settings only
        configure_smtp()

    elif choice == "5":
        # Complete reconfiguration
        setup_complete_config()

    elif choice == "6":
        print("Exiting.")
        return

    else:
        print("Invalid choice. Exiting.")
        return

    print(
        "\nRun 'uv run python main.py check' to check aurora "
        "visibility and get notified."
    )


def test_email() -> None:
    """Test email configuration by sending a test message.

    Loads the current configuration, extracts email addresses,
    and sends a test email to all configured recipients to verify
    SMTP settings are working correctly.

    Raises:
        SystemExit: If no email addresses are configured
    """
    config = load_config()

    # Support both old single email and new multiple emails format
    emails = config.get(
        "emails", [config.get("email")] if config.get("email") else []
    )

    if not emails:
        print("Error: No email addresses configured.")
        print(
            "Run 'uv run python main.py configure' to set up email addresses."
        )
        return

    print("Testing email configuration...")
    print(f"Sending test email to: {', '.join(emails)}")

    # Get locations for the email
    locations = config.get("locations", [])
    if not locations and "city" in config:
        # Old format
        locations = [{
            "city": config["city"],
            "country": config["country"],
            "latitude": config["latitude"],
            "longitude": config["longitude"]
        }]

    # Generate formatted email
    plain_body, html_body = create_test_email(locations)

    subject = "Northern Lights - Email Test"

    for email in emails:
        send_email(email, subject, plain_body, html_body)

    print(
        f"\nTest email sent to {len(emails)} recipient(s)! Check your inbox."
    )


def list_config() -> None:
    """Display current configuration.

    Shows all configured locations with their coordinates,
    email recipients, and SMTP configuration status.
    Supports both old (single location/email) and new
    (multiple locations/emails) configuration formats.
    """
    if not config_exists():
        print("No configuration file found.")
        print("Run 'uv run python main.py configure' to create one.")
        return

    config = load_config()

    print("\n=== Current Configuration ===\n")

    # Show locations
    if "locations" in config:
        print(f"Locations ({len(config['locations'])}):")
        for i, loc in enumerate(config["locations"], 1):
            print(f"  {i}. {loc['city']}, {loc['country']}")
            coords = f"{loc['latitude']:.4f}, {loc['longitude']:.4f}"
            print(f"     Coordinates: {coords}")
    elif "city" in config:
        # Old single location format
        print("Location:")
        print(f"  {config['city']}, {config['country']}")
        lat = config.get('latitude', 'N/A')
        lng = config.get('longitude', 'N/A')
        print(f"  Coordinates: {lat}, {lng}")

    # Show emails
    print()
    if "emails" in config:
        print(f"Email Recipients ({len(config['emails'])}):")
        for i, email in enumerate(config["emails"], 1):
            print(f"  {i}. {email}")
    elif "email" in config:
        print("Email Recipient:")
        print(f"  {config['email']}")
    else:
        print("Email Recipients: (none configured)")

    # Show notification threshold
    print()
    threshold = config.get("notification_threshold", "HIGH")
    print(f"Notification Threshold: {threshold}")

    # Show SMTP status
    print()
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        print("SMTP Configuration: Configured (.env file found)")
    else:
        print("SMTP Configuration: Not configured")

    print()


def check(save_output: str = None) -> None:
    """Check aurora visibility and send notification if HIGH.

    Args:
        save_output: Optional path to save raw API responses

    Sends email if visibility is HIGH at any configured location.
    """
    config: Dict[str, Any] = load_config()

    # Get locations (support both old and new format)
    locations: List[Dict[str, Any]] = config.get("locations", [])
    if not locations and "city" in config:
        # Convert old single location format
        locations = [
            {
                "city": config["city"],
                "country": config["country"],
                "latitude": config["latitude"],
                "longitude": config["longitude"],
            }
        ]

    if not locations:
        print(
            "No locations configured. Run 'uv run python main.py "
            "configure' to add locations."
        )
        return

    # Get emails
    emails: List[str] = config.get(
        "emails", [config.get("email")] if config.get("email") else []
    )
    if not emails:
        print(
            "Warning: No email addresses configured. "
            "Run 'uv run python main.py configure'."
        )
        return

    # Get notification threshold
    threshold = config.get("notification_threshold", "HIGH")

    # Determine KP threshold based on setting
    if threshold == "MODERATE":
        kp_threshold = 3.0
        threshold_desc = "KP >= 3.0"
    elif threshold == "ALL":
        kp_threshold = 0.0
        threshold_desc = "KP > 0"
    else:  # HIGH
        kp_threshold = 5.0
        threshold_desc = "KP >= 5.0"

    print(
        f"Checking aurora visibility for {len(locations)} location(s)...\n"
        f"Notification threshold: {threshold} ({threshold_desc})\n"
    )

    notification_locations: List[Tuple[Dict[str, Any], float]] = []

    # Check each location
    for loc in locations:
        data = fetch_aurora_data(
            loc["latitude"], loc["longitude"], save_output=save_output
        )

        # Try to get KP index from API response
        kp_index = None
        if "ace" in data:
            kp_index = data["ace"].get("kp")
            if kp_index is None and "current" in data["ace"]:
                kp_index = data["ace"]["current"].get("kp")

        if kp_index is None:
            location_name = f"{loc['city']}, {loc['country']}"
            print(f"⚠ {location_name}: Unable to determine KP index")
            continue

        kp_value = float(kp_index)

        # Print status
        location_name = f"{loc['city']}, {loc['country']}"
        if kp_value >= 5:
            print(f"✓ {location_name}: KP {kp_value} - HIGH visibility!")
            if kp_value >= kp_threshold:
                notification_locations.append((loc, kp_value))
        elif kp_value >= 3:
            print(f"○ {location_name}: KP {kp_value} - MODERATE visibility")
            if kp_value >= kp_threshold:
                notification_locations.append((loc, kp_value))
        else:
            print(f"  {location_name}: KP {kp_value} - LOW visibility")
            if kp_value > 0 and kp_value >= kp_threshold:
                notification_locations.append((loc, kp_value))

    # Send notification if any location meets threshold
    if notification_locations:
        print(f"\nSending notification to {len(emails)} recipient(s)...")

        # Generate formatted email
        plain_body, html_body = create_aurora_alert_email(
            notification_locations
        )

        # Create subject line
        if len(notification_locations) == 1:
            loc, kp = notification_locations[0]
            subject = f"Aurora Alert: Visibility at {loc['city']}"
        else:
            num_locs = len(notification_locations)
            subject = (
                f"Aurora Alert: Visibility at "
                f"{num_locs} location(s)"
            )

        for email in emails:
            send_email(email, subject, plain_body, html_body)

        num_notified = len(notification_locations)
        print(f"Notification sent for {num_notified} location(s)!")
    else:
        print(
            f"\nNo locations meet notification threshold "
            f"({threshold_desc})"
        )
