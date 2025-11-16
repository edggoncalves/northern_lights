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
            "Usage: python main.py <command> [options]\n\n"
            "Commands:\n"
            "  configure   - Set up your locations and email settings\n"
            "  list        - Show current configuration\n"
            "  check       - Check aurora visibility at all locations\n"
            "  test-email  - Send a test email to verify SMTP configuration\n\n"
            "Options for 'check' command:\n"
            "  --save-output <file>  - Save raw API responses to file"
        )

    command = sys.argv[1]
    if command == "configure":
        configure()
    elif command == "list":
        list_config()
    elif command == "check":
        # Parse optional --save-output flag
        save_output = None
        if len(sys.argv) > 2 and sys.argv[2] == "--save-output":
            if len(sys.argv) > 3:
                save_output = sys.argv[3]
            else:
                sys.exit("Error: --save-output requires a file path argument")
        check(save_output=save_output)
    elif command == "test-email":
        test_email()
    else:
        sys.exit(
            f"Invalid command: {command}\n"
            "Valid commands: configure, list, check, test-email"
        )


if __name__ == "__main__":
    main()
