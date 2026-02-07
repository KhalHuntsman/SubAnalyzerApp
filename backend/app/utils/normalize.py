#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

import re


def normalize_merchant(raw: str) -> str:
    """
    Normalize a merchant string for grouping transactions.
    Converts text to uppercase, removes punctuation,
    strips long numeric tokens, and collapses whitespace.
    """

    if not raw:
        return "UNKNOWN"

    # Convert to uppercase
    text = raw.upper()

    # Replace punctuation with spaces
    text = re.sub(r"[^A-Z0-9\s]", " ", text)

    # Remove long standalone numbers (often store IDs)
    text = re.sub(r"\b\d{2,}\b", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return "UNKNOWN"

    # Limit stored length
    return text[:160]
