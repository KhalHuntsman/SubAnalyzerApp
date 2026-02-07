#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from datetime import datetime
from decimal import Decimal, InvalidOperation


def parse_date(value: str):
    """
    Parse a date string in either:
    - MM/DD/YYYY (preferred)
    - YYYY-MM-DD (fallback)

    Returns a date object.
    """

    if not value:
        raise ValueError("Date is required.")

    value = value.strip()

    # Try MM/DD/YYYY first
    try:
        return datetime.strptime(value, "%m/%d/%Y").date()
    except ValueError:
        pass

    # Fallback to ISO format
    try:
        return datetime.fromisoformat(value).date()
    except Exception:
        raise ValueError("Invalid date format. Use MM/DD/YYYY.")



def parse_amount(value):
    """
    Convert a numeric value into a Decimal with two decimal places.
    Raises ValueError if invalid or non-positive.
    """

    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid amount.")

    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    return amount
