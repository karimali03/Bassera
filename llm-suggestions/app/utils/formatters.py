"""Formatting utilities for amounts and dates."""

from datetime import datetime


def format_egp(amount: float) -> str:
    """Format a float as a human-readable EGP string. E.g. 1234.5 → 'EGP 1,234.50'"""
    return f"EGP {amount:,.2f}"


def format_period(start: datetime, end: datetime) -> str:
    return f"{start.strftime('%d %b')} – {end.strftime('%d %b %Y')}"
