"""Northern Lights - Aurora Borealis visibility tracker.

This CLI tool checks aurora visibility and sends email notifications
when conditions are favorable for viewing the Northern Lights.
"""

import sys

from utils.cli_commands import configure, test_email, list_config, check
from utils.logger import setup_logger


def main() -> None:
    """Main entry point for the CLI."""
    # Initialize logging
    setup_logger()
    if not sys.argv[1:]:
        sys.exit(
            "Usage: python main.py <command>\n"
            "Commands:\n"
            "  configure  - Set up your locations and email settings\n"
            "  list       - Show current configuration\n"
            "  check      - Check aurora visibility at all locations\n"
            "  test-email - Send a test email to verify SMTP configuration"
        )

    command = sys.argv[1]
    if command == "configure":
        configure()
    elif command == "list":
        list_config()
    elif command == "check":
        check()
    elif command == "test-email":
        test_email()
    else:
        sys.exit(
            f"Invalid command: {command}\n"
            "Valid commands: configure, list, check, test-email"
        )


if __name__ == "__main__":
    main()
