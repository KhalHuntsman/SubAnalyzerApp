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
    """Convert an amount + cadence into a monthly-equivalent cost."""
    if cadence == "weekly":
        return amount * 52 / 12
    if cadence == "monthly":
        return amount
    if cadence == "quarterly":
        return amount / 3
    if cadence == "yearly":
        return amount / 12

    return amount


@bp.get("")
@jwt_required()
def dashboard():
    """Return a summary of active subscriptions and upcoming charges."""
    user_id = int(get_jwt_identity())

    subscriptions = Subscription.query.filter_by(
        user_id=user_id,
        status="active"
    ).all()

    monthly_total = 0.0
    annual_total = 0.0

    upcoming = []
    today = date.today()
    window_end = today + timedelta(days=30)

    for sub in subscriptions:
        amount = float(sub.amount)

        monthly_total += _monthly_equivalent(amount, sub.cadence)
        annual_total += _monthly_equivalent(amount, sub.cadence) * 12

        if today <= sub.next_due_date <= window_end:
            upcoming.append({
                "subscription_id": sub.id,
                "name": sub.name,
                "amount": amount,
                "due_date": sub.next_due_date.isoformat(),
                "cadence": sub.cadence,
            })

    upcoming.sort(key=lambda x: x["due_date"])

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
