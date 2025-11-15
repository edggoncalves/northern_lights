# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Northern Lights is a Python CLI tool that checks aurora borealis visibility at a user's location and sends email notifications when viewing conditions are favorable. It uses geopy for geocoding and the Auroras.live API to fetch KP index data (a measure of geomagnetic activity ranging from 0-9).

**Powered by [Auroras.live](https://auroras.live)**

## Architecture

The project follows a modular structure with utility functions separated into the [utils/](utils/) directory:

- [main.py](main.py) - Minimal CLI entry point (40 lines) - argument parsing and command dispatch only
- [utils/cli_commands.py](utils/cli_commands.py) - CLI command implementations (`configure`, `list`, `check`, `test-email`)
- [utils/config.py](utils/config.py) - Configuration management (load, save, interactive setup, location/email management)
- [utils/geocoding.py](utils/geocoding.py) - Geocoding using geopy's Nominatim service
- [utils/aurora_api.py](utils/aurora_api.py) - Client for Auroras.live API
- [utils/email_notifier.py](utils/email_notifier.py) - SMTP email notification functionality

### Key Design Decisions

- **Package management**: Uses uv for fast, reliable dependency management
- **Modular structure**: Functions are organized by concern to avoid import issues and improve maintainability
- **Configuration**: Stores multiple locations (city, country, lat/lng) and email recipients in `config.json` (gitignored). Supports monitoring multiple locations simultaneously.
- **Email credentials**: Stored in `.env` file (gitignored) and loaded via python-dotenv
- **Email notifications**: Only sent when KP index >= 5 (high visibility)
- **Error handling**: All external calls (geocoding, API, SMTP) have proper error handling with informative messages

## Development Commands

### Setup

```bash
# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### Running the Application

```bash
# First-time setup: configure locations and email
# Presents menu to configure specific settings or all at once
uv run python main.py configure

# View current configuration
uv run python main.py list

# Test email configuration (optional)
uv run python main.py test-email

# Check aurora visibility at all locations (sends email if KP >= 5 anywhere)
uv run python main.py check

# Or activate the virtual environment first
source .venv/bin/activate
python main.py configure
python main.py test-email
python main.py check
```

### Configuration Options

The `configure` command provides an interactive menu to update settings individually:

1. **Locations** - Add, remove, or view monitoring locations (supports multiple)
2. **Email recipients** - Add/change notification email addresses (supports multiple)
3. **SMTP settings** - Configure email server credentials
4. **All settings** - Complete reconfiguration
5. **Exit** - Cancel changes

The `list` command displays your current configuration:

- All configured locations with coordinates
- All email recipients
- SMTP configuration status

This allows you to view or update individual settings without reconfiguring everything.

### Email Notifications

SMTP credentials are stored in a `.env` file. If not configured yet, you can:

1. Run `python main.py configure` again to set up the `.env` file
2. Manually create a `.env` file with:

   ```text
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

3. Set environment variables directly in your shell

If SMTP credentials are not configured, the script will print what the email would contain instead of sending it.

### Automated Checks with Cron

To automatically check aurora visibility on a schedule (e.g., daily at 8 PM), set up a cronjob:

```bash
# Example: Check daily at 8 PM
0 20 * * * cd /path/to/northern_lights && /path/to/uv run python main.py check
```

**Resources:**

- [How to create a cronjob](https://www.cyberciti.biz/faq/how-do-i-add-jobs-to-cron-under-linux-or-unix-oses/)
- [Cron schedule generator](https://crontab.guru/)

## Implementation Notes

- **API Endpoint**: The Auroras.live API endpoint (`http://api.auroras.live/v1/`) uses HTTP, not HTTPS
- **Geocoding User Agent**: Uses "northern-lights-tracker" as required by Nominatim terms of service
- **Multiple Locations**: Monitor aurora visibility at multiple locations simultaneously (home, cabin, vacation spots, etc.)
- **Multiple Recipients**: Sends notifications to multiple email addresses
- **Smart Notifications**: Email sent if ANY monitored location has high visibility, listing all locations with KP >= 5
- **Backward Compatibility**: Automatically supports old config files with single location/email fields
- **KP Index Thresholds**:
  - KP >= 5: HIGH visibility (excellent chance) - **email notification sent**
  - KP >= 3: MODERATE visibility (worth checking) - no notification
  - KP < 3: LOW visibility - no notification
- **Cron Setup**: The `check` command is designed to be run via cron/scheduler to automate daily checks

## Dependencies

- `requests` - HTTP requests to Auroras.live API
- `geopy` - Geocoding service (Nominatim)
- `python-dotenv` - Load SMTP credentials from .env file
- `rich` - Listed in pyproject.toml but not currently used (reserved for future formatting improvements)

## Project Structure

```text
northern_lights/
├── main.py              # CLI entry point (40 lines - minimal)
├── utils/               # Utility modules
│   ├── __init__.py
│   ├── cli_commands.py  # CLI command implementations
│   ├── config.py        # Config management (load, save, interactive setup)
│   ├── geocoding.py     # Location to coordinates
│   ├── aurora_api.py    # API client
│   └── email_notifier.py # Email sending
├── config.json          # User config (gitignored)
├── .env                 # SMTP credentials (gitignored)
├── .venv/               # Virtual environment (gitignored)
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Lockfile for reproducible builds
└── README.md            # User-facing documentation
```
