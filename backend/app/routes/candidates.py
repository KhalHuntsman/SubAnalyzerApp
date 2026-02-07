#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import db
from ..models.candidate import RecurringCandidate
from ..models.subscription import Subscription, ALLOWED_CADENCES
from ..utils.validation import parse_amount
from ..utils.normalize import normalize_merchant


# Blueprint for recurring candidate routes
bp = Blueprint("candidates", __name__)


@bp.get("")
@jwt_required()
def list_candidates():
    """Return candidates filtered by status."""
    user_id = int(get_jwt_identity())
    status = request.args.get("status", "pending")

    query = RecurringCandidate.query.filter_by(user_id=user_id)

    if status:
        query = query.filter_by(status=status)

    candidates = query.order_by(
        RecurringCandidate.confidence.desc()
    ).all()

    return jsonify([c.to_dict() for c in candidates])


@bp.patch("/<int:cand_id>")
@jwt_required()
def update_candidate(cand_id):
    """Edit candidate fields or update status."""
    user_id = int(get_jwt_identity())

    candidate = RecurringCandidate.query.get(cand_id)

    if not candidate or candidate.user_id != user_id:
        return jsonify({"error": "Candidate not found."}), 404

    data = request.get_json(silent=True) or {}

    # Update display name and merchant key
    if "display_name" in data:
        name = (data.get("display_name") or "").strip()

        if not name:
            return jsonify({"error": "display_name cannot be empty."}), 400

        candidate.display_name = name
        candidate.merchant_key = normalize_merchant(name)

    # Update amount
    if "avg_amount" in data:
        try:
            candidate.avg_amount = parse_amount(data.get("avg_amount"))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # Update cadence guess
    if "cadence_guess" in data:
        cadence = (data.get("cadence_guess") or "").strip().lower()

        if cadence not in ALLOWED_CADENCES:
            return jsonify({
                "error": f"cadence_guess must be one of: {sorted(ALLOWED_CADENCES)}"
            }), 400

        candidate.cadence_guess = cadence

    # Update workflow status
    if "status" in data:
        status_value = (data.get("status") or "").strip().lower()

        if status_value not in {"pending", "confirmed", "ignored"}:
            return jsonify({
                "error": "status must be pending, confirmed, or ignored."
            }), 400

        candidate.status = status_value

    db.session.commit()

    return jsonify(candidate.to_dict())


@bp.post("/<int:cand_id>/confirm")
@jwt_required()
def confirm_candidate(cand_id):
    """Convert a candidate into a subscription."""
    user_id = int(get_jwt_identity())

    candidate = RecurringCandidate.query.get(cand_id)

    if not candidate or candidate.user_id != user_id:
        return jsonify({"error": "Candidate not found."}), 404

    if candidate.status != "pending":
        return jsonify({
            "error": "Only pending candidates can be confirmed."
        }), 400

    # Create a new subscription from candidate data
    subscription = Subscription(
        user_id=user_id,
        name=candidate.display_name,
        merchant_key=candidate.merchant_key,
        amount=candidate.avg_amount,
        cadence=candidate.cadence_guess,
        next_due_date=candidate.next_predicted,
        category=None,
        notes=(
            f"Created from detected recurring candidate "
            f"(confidence={candidate.confidence})."
        ),
        status="active",
    )

    db.session.add(subscription)
    db.session.flush()  # Assign ID before committing

    # Mark candidate as confirmed
    candidate.status = "confirmed"
    candidate.confirmed_subscription_id = subscription.id

    db.session.commit()

    return jsonify({
        "subscription": subscription.to_dict(),
        "candidate": candidate.to_dict()
    }), 201


@bp.delete("/<int:cand_id>")
@jwt_required()
def delete_candidate(cand_id):
    """Delete a candidate."""
    user_id = int(get_jwt_identity())

    candidate = RecurringCandidate.query.get(cand_id)

    if not candidate or candidate.user_id != user_id:
        return jsonify({"error": "Candidate not found."}), 404

    db.session.delete(candidate)
    db.session.commit()

    return jsonify({"deleted": True})
