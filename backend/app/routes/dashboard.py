#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from datetime import date, timedelta
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.subscription import Subscription


# Blueprint for dashboard summary routes
bp = Blueprint("dashboard", __name__)


def _monthly_equivalent(amount: float, cadence: str) -> float:
    """Convert an amount + cadence into a monthly-equivalent cost.

    Note: weekly uses 52/12 as an approximation (not 365.25/7), which is fine for
    budgeting summaries but will never be perfectly exact month-to-month.
    """
    if cadence == "weekly":
        return amount * 52 / 12
    if cadence == "monthly":
        return amount
    if cadence == "quarterly":
        return amount / 3
    if cadence == "yearly":
        return amount / 12

    # Fallback: treat unknown cadence as monthly to avoid breaking the dashboard.
    return amount


@bp.get("")
@jwt_required()
def dashboard():
    """Return a summary of active subscriptions and upcoming charges."""
    user_id = int(get_jwt_identity())

    # Dashboard only considers active subscriptions to match the user's "current spend".
    subscriptions = Subscription.query.filter_by(
        user_id=user_id,
        status="active"
    ).all()

    monthly_total = 0.0
    annual_total = 0.0

    upcoming = []
    today = date.today()
    window_end = today + timedelta(days=30)  # Rolling 30-day window for "upcoming" charges.

    for sub in subscriptions:
        amount = float(sub.amount)

        # Compute totals in a cadence-agnostic way using monthly equivalents.
        monthly_equiv = _monthly_equivalent(amount, sub.cadence)
        monthly_total += monthly_equiv
        annual_total += monthly_equiv * 12

        # Upcoming charges are based on the stored next_due_date (no recurrence expansion here).
        if today <= sub.next_due_date <= window_end:
            upcoming.append({
                "subscription_id": sub.id,
                "name": sub.name,
                "amount": amount,
                "due_date": sub.next_due_date.isoformat(),
                "cadence": sub.cadence,
            })

    # Sort by ISO date string for stable chronological ordering.
    upcoming.sort(key=lambda x: x["due_date"])

    # Surface the highest nominal charge amounts (not monthly-equivalent) for quick visibility.
    top_subs = sorted(
        subscriptions,
        key=lambda s: float(s.amount),
        reverse=True
    )[:5]

    top_list = [
        {
            "id": s.id,
            "name": s.name,
            "amount": float(s.amount),
            "cadence": s.cadence
        }
        for s in top_subs
    ]

    return jsonify({
        "monthly_total": round(monthly_total, 2),
        "annual_total": round(annual_total, 2),
        "active_count": len(subscriptions),
        "upcoming_30_days": upcoming,
        "top_subscriptions": top_list,
    })
