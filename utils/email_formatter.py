"""Email formatting utilities using Rich for beautiful emails."""

from typing import List, Dict, Any, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from io import StringIO


def create_aurora_alert_email(
    high_visibility_locations: List[Tuple[Dict[str, Any], float]]
) -> Tuple[str, str]:
    """Create a beautifully formatted aurora alert email.

    Args:
        high_visibility_locations: List of (location_dict, kp_value) tuples

    Returns:
        Tuple of (plain_text_body, html_body)
    """
    # Create Rich console for rendering
    console = Console(
        file=StringIO(),
        record=True,
        force_terminal=True,
        width=80
    )

    # Header with emoji
    console.print()
    header = Text(
        "🌌 Aurora Borealis Alert 🌌",
        style="bold cyan",
        justify="center"
    )
    console.print(
        Panel(
            header,
            style="green",
            border_style="green",
            padding=(1, 2)
        )
    )
    console.print()

    # Main message
    console.print(
        "[bold green]Great news! High visibility "
        "auroras detected![/bold green]",
        justify="center"
    )
    console.print()

    # Create table for locations
    table = Table(
        title="[bold]🎆 High Visibility Locations[/bold]",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title_style="bold",
        show_lines=True
    )
    table.add_column("📍 Location", style="cyan", no_wrap=False)
    table.add_column("🗺️  Coordinates", style="dim", justify="center")
    table.add_column(
        "⚡ KP Index",
        style="bold green",
        justify="center"
    )

    for loc, kp in high_visibility_locations:
        coords = f"{loc['latitude']:.4f}°, {loc['longitude']:.4f}°"
        table.add_row(
            f"{loc['city']}, {loc['country']}",
            coords,
            f"[bold]{kp}[/bold]"
        )

    console.print(table)
    console.print()

    # Call to action
    console.print(
        Panel(
            "[bold]Get outside and look up at the sky! "
            "Tonight could be spectacular! ✨[/bold]",
            style="blue",
            border_style="blue"
        )
    )
    console.print()

    # Footer
    console.print(
        "[dim italic]Automated notification from "
        "Northern Lights Tracker[/dim italic]",
        justify="center"
    )
    console.print()

    # Get HTML export
    html_body = console.export_html(inline_styles=True)

    # Create plain text version
    plain_text = _create_plain_text_alert(high_visibility_locations)

    return plain_text, html_body


def create_test_email(
    locations: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """Create a beautifully formatted test email.

    Args:
        locations: List of location dictionaries

    Returns:
        Tuple of (plain_text_body, html_body)
    """
    # Create Rich console for rendering
    console = Console(
        file=StringIO(),
        record=True,
        force_terminal=True,
        width=80
    )

    # Header
    console.print()
    header = Text(
        "Northern Lights Email Test",
        style="bold cyan",
        justify="center"
    )
    console.print(
        Panel(
            header,
            style="blue",
            border_style="blue",
            padding=(1, 2)
        )
    )
    console.print()

    # Success message
    console.print(
        "[bold green]✓ SMTP Configuration Successful![/bold green]",
        justify="center"
    )
    console.print()

    # Location table
    table = Table(
        title="[bold]📍 Monitoring Locations[/bold]",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        show_lines=True
    )
    table.add_column("City", style="cyan", no_wrap=False)
    table.add_column("Country", style="cyan")
    table.add_column("Coordinates", style="dim", justify="center")

    for loc in locations:
        coords = f"{loc['latitude']:.4f}°, {loc['longitude']:.4f}°"
        table.add_row(loc['city'], loc['country'], coords)

    console.print(table)
    console.print()

    # Info panel
    console.print(
        Panel(
            "You will receive alerts when aurora visibility is HIGH\n"
            "(KP index ≥ 5.0) at any monitored location.",
            title="[bold]ℹ️  Alert Settings[/bold]",
            style="blue",
            border_style="blue"
        )
    )
    console.print()

    # Footer
    console.print(
        "[dim italic]Test email from Northern Lights Tracker[/dim italic]",
        justify="center"
    )
    console.print()

    # Get HTML export
    html_body = console.export_html(inline_styles=True)

    # Create plain text version
    plain_text = _create_plain_text_test(locations)

    return plain_text, html_body


def _create_plain_text_alert(
    high_visibility_locations: List[Tuple[Dict[str, Any], float]]
) -> str:
    """Create plain text version of aurora alert.

    Args:
        high_visibility_locations: List of (location_dict, kp_value) tuples

    Returns:
        Plain text email body
    """
    lines = [
        "Aurora Borealis Visibility Alert",
        "=" * 50,
        "",
        "Great chance to see auroras tonight!",
        "",
        "High Visibility Locations:",
        ""
    ]

    for loc, kp in high_visibility_locations:
        lines.append(f"📍 {loc['city']}, {loc['country']}")
        lines.append(
            f"   Coordinates: {loc['latitude']:.4f}, "
            f"{loc['longitude']:.4f}"
        )
        lines.append(f"   KP Index: {kp}")
        lines.append("")

    lines.extend([
        "Get outside and look up! 🌌",
        "",
        "This is an automated notification from Northern Lights tracker."
    ])

    return "\n".join(lines)


def _create_plain_text_test(locations: List[Dict[str, Any]]) -> str:
    """Create plain text version of test email.

    Args:
        locations: List of location dictionaries

    Returns:
        Plain text email body
    """
    lines = [
        "Northern Lights - Email Test",
        "=" * 50,
        "",
        "✓ SMTP Configuration Test Successful!",
        "",
        "Configured Locations:",
        ""
    ]

    for loc in locations:
        lines.append(f"  • {loc['city']}, {loc['country']}")
        lines.append(
            f"    {loc['latitude']:.4f}, {loc['longitude']:.4f}"
        )

    lines.extend([
        "",
        "You will receive aurora alerts when the KP index reaches "
        "5.0 or higher.",
        "",
        "This is a test email from Northern Lights tracker."
    ])

    return "\n".join(lines)
