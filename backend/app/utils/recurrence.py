#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from statistics import median


@dataclass
class CandidateResult:
    """Structured result returned by the detection algorithm."""

    merchant_key: str
    display_name: str
    avg_amount: float
    cadence_guess: str
    confidence: float
    last_seen: date
    next_predicted: date


def _cadence_from_gaps(gaps: list[int]) -> tuple[str | None, float]:
    """
    Estimate billing cadence from time gaps between charges.
    Returns (cadence, confidence_score).
    """

    if not gaps:
        return None, 0.0

    med = median(gaps)

    # Known cadence targets and tolerance ranges
    # Monthly is intentionally wider because real billing varies (28-35 days)
    buckets = [
        ("weekly", 7, 2),
        ("monthly", 30, 7),
        ("quarterly", 91, 12),
        ("yearly", 365, 25),
    ]

    for name, target, tolerance in buckets:
        if abs(med - target) <= tolerance:
            within = sum(
                1 for g in gaps
                if abs(g - target) <= tolerance
            )

            confidence = within / max(1, len(gaps))
            return name, confidence

    return None, 0.0


def _amount_stability(amounts: list[float], tolerance_ratio: float = 0.12) -> float:
    """
    Measure how consistent charge amounts are.
    Returns a stability score between 0 and 1.
    """

    if not amounts:
        return 0.0

    med = median(amounts)

    if med == 0:
        return 0.0

    tolerance = abs(med) * tolerance_ratio

    within = sum(
        1 for amt in amounts
        if abs(amt - med) <= tolerance
    )

    return within / max(1, len(amounts))


def _merchant_signal(merchant_key: str, display_name: str) -> float:
    """
    Heuristic scoring to boost subscription-like merchants and penalize obvious non-subscription merchants.
    Returns a multiplier-ish score centered around 1.0.
    """

    text = f"{merchant_key} {display_name}".lower()

    boost_keywords = [
        "netflix", "hulu", "spotify", "pandora", "apple", "icloud", "itunes", "app store",
        "max", "hbomax", "disney", "prime", "amazon prime", "youtube", "yt premium",
        "spectrum", "comcast", "xfinity", "verizon", "att", "tmobile", "internet",
        "electric", "energy", "water", "utility", "sewer", "gas",
        "insurance", "premium", "geico", "progressive", "state farm",
        "membership", "subscription", "billing", "recurring",
        "loan", "car payment", "lease",
        "capital one", "discover", "chase", "credit one", "amex",
    ]

    penalty_keywords = [
        "doordash", "uber", "ubereats", "grubhub",
        "mcdonald", "wendy", "taco", "domino", "pizza", "kfc", "burger", "chipotle", "papa", "subway", "sonic",
        "restaurant", "grill", "cafe", "bar", "steakhouse",
        "meijer", "walmart", "target", "marathon", "shell", "bp",
        "service fee", "transfer", "fee"
    ]

    score = 1.0

    if any(k in text for k in boost_keywords):
        score += 0.25

    if any(k in text for k in penalty_keywords):
        score -= 0.35

    # Clamp to a reasonable range
    if score < 0.5:
        score = 0.5
    if score > 1.25:
        score = 1.25

    return score


def _predict_next(last_seen: date, cadence: str) -> date:
    """Predict the next charge date from cadence."""
    if cadence == "weekly":
        return last_seen + timedelta(days=7)
    if cadence == "monthly":
        return last_seen + timedelta(days=30)
    if cadence == "quarterly":
        return last_seen + timedelta(days=91)
    return last_seen + timedelta(days=365)


def detect_recurring(
    merchant_key: str,
    display_name: str,
    charges: list[tuple[date, float]],
) -> CandidateResult | None:
    """
    Detect recurring billing patterns for a merchant.
    Returns a CandidateResult if detected, otherwise None.
    """

    # Sort charges by date
    sorted_charges = sorted(charges, key=lambda x: x[0])

    if len(sorted_charges) < 2:
        return None

    dates = [d for d, _ in sorted_charges]
    amounts = [float(a) for _, a in sorted_charges]

    # Calculate day gaps between consecutive charges
    gaps = [
        (dates[i] - dates[i - 1]).days
        for i in range(1, len(dates))
    ]

    cadence, cadence_score = _cadence_from_gaps(gaps)

    if cadence is None:
        return None

    amount_score = _amount_stability(amounts)

    # Evidence factor: fewer occurrences => lower confidence ceiling
    # 2 charges => weaker evidence, 3+ charges => full strength
    n = len(sorted_charges)
    if n >= 5:
        evidence = 1.0
    elif n == 4:
        evidence = 0.9
    elif n == 3:
        evidence = 0.8
    else:
        evidence = 0.6

    # Merchant signal helps filter obvious false positives (food/delivery)
    merchant_factor = _merchant_signal(merchant_key, display_name)

    # Weighted confidence score
    # Increase weight on cadence (most important signal), but keep amount as supporting signal.
    base_confidence = (0.75 * cadence_score) + (0.25 * amount_score)
    confidence = round(base_confidence * evidence * merchant_factor, 4)

    # Thresholds:
    # - With 2 occurrences we allow only stronger merchant signals (factor > 0.95) and higher cadence score
    if n == 2:
        if merchant_factor < 0.95 or cadence_score < 1.0:
            return None
        if confidence < 0.45:
            return None
    else:
        if confidence < 0.50:
            return None

    avg_amount = float(
        round(Decimal(str(median(amounts))), 2)
    )

    last_seen = dates[-1]
    next_predicted = _predict_next(last_seen, cadence)

    return CandidateResult(
        merchant_key=merchant_key,
        display_name=display_name,
        avg_amount=avg_amount,
        cadence_guess=cadence,
        confidence=confidence,
        last_seen=last_seen,
        next_predicted=next_predicted,
    )
