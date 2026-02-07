#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import db
from ..models.subscription import Subscription, ALLOWED_CADENCES
from ..utils.normalize import normalize_merchant
from ..utils.validation import parse_date, parse_amount


# Blueprint for subscription CRUD routes
bp = Blueprint("subscriptions", __name__)


@bp.get("")
@jwt_required()
def list_subscriptions():
    """Return subscriptions for the current user."""
    user_id = int(get_jwt_identity())
    status = request.args.get("status")

    query = Subscription.query.filter_by(user_id=user_id)

    # Optional status filter supports UI tabs (active vs canceled).
    if status:
        query = query.filter_by(status=status)

    subs = query.order_by(Subscription.created_at.desc()).all()

    return jsonify([s.to_dict() for s in subs])


@bp.post("")
@jwt_required()
def create_subscription():
    """Create a new subscription."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    cadence = (data.get("cadence") or "").strip().lower()
    next_due_date = data.get("next_due_date")

    category = (data.get("category") or "").strip() or None
    notes = (data.get("notes") or "").strip() or None

    if not name:
        return jsonify({"error": "Name is required."}), 400

    if cadence not in ALLOWED_CADENCES:
        return jsonify({
            "error": f"Cadence must be one of: {sorted(ALLOWED_CADENCES)}"
        }), 400

    try:
        amount = parse_amount(data.get("amount"))
        next_date = parse_date(next_due_date)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Merchant key is used for grouping/detection; deriving from name keeps behavior consistent
    # even when the user manually creates/edit subscriptions.
    merchant_key = normalize_merchant(name)

    sub = Subscription(
        user_id=user_id,
        name=name,
        merchant_key=merchant_key,
        amount=amount,
        cadence=cadence,
        next_due_date=next_date,
        category=category,
        notes=notes,
        status="active",
    )

    db.session.add(sub)
    db.session.commit()

    return jsonify(sub.to_dict()), 201


@bp.patch("/<int:sub_id>")
@jwt_required()
def update_subscription(sub_id):
    """Partially update subscription fields (PATCH)."""
    user_id = int(get_jwt_identity())

    sub = Subscription.query.get(sub_id)

    if not sub or sub.user_id != user_id:
        return jsonify({"error": "Subscription not found."}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = (data.get("name") or "").strip()

        if not name:
            return jsonify({"error": "Name cannot be empty."}), 400

        sub.name = name
        sub.merchant_key = normalize_merchant(name)  # Keep grouping key in sync with visible name.

    if "amount" in data:
        try:
            sub.amount = parse_amount(data.get("amount"))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if "cadence" in data:
        cadence = (data.get("cadence") or "").strip().lower()

        if cadence not in ALLOWED_CADENCES:
            return jsonify({
                "error": f"Cadence must be one of: {sorted(ALLOWED_CADENCES)}"
            }), 400

        sub.cadence = cadence

    if "next_due_date" in data:
        try:
            sub.next_due_date = parse_date(data.get("next_due_date"))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if "category" in data:
        sub.category = (data.get("category") or "").strip() or None

    if "notes" in data:
        sub.notes = (data.get("notes") or "").strip() or None

    if "status" in data:
        status = (data.get("status") or "").strip().lower()

        if status not in {"active", "canceled"}:
            return jsonify({"error": "Status must be active or canceled."}), 400

        sub.status = status

    db.session.commit()

    return jsonify(sub.to_dict())


@bp.delete("/<int:sub_id>")
@jwt_required()
def delete_subscription(sub_id):
    """Delete a subscription."""
    user_id = int(get_jwt_identity())

    sub = Subscription.query.get(sub_id)

    if not sub or sub.user_id != user_id:
        return jsonify({"error": "Subscription not found."}), 404

    db.session.delete(sub)
    db.session.commit()

    return jsonify({"deleted": True})
