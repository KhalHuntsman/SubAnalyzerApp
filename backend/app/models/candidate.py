#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from datetime import datetime
from .. import db


class RecurringCandidate(db.Model):
    __tablename__ = "recurring_candidates"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking this candidate to a user
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Normalized merchant identifier used for grouping transactions
    merchant_key = db.Column(
        db.String(160),
        nullable=False,
        index=True
    )

    # Display name shown to the user
    display_name = db.Column(
        db.String(160),
        nullable=False
    )

    # Estimated recurring payment amount
    avg_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    # Predicted billing cadence
    cadence_guess = db.Column(
        db.String(20),
        nullable=False
    )

    # Confidence score from the detection algorithm
    confidence = db.Column(
        db.Float,
        nullable=False
    )

    # Most recent detected charge date
    last_seen = db.Column(
        db.Date,
        nullable=False
    )

    # Predicted next charge date
    next_predicted = db.Column(
        db.Date,
        nullable=False
    )

    # Current workflow state of the candidate
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    # Linked subscription ID after confirmation
    confirmed_subscription_id = db.Column(
        db.Integer,
        nullable=True
    )

    # Timestamp tracking
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship back to the owning user
    user = db.relationship(
        "User",
        back_populates="candidates"
    )

    def to_dict(self):
        """Convert model instance to a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "merchant_key": self.merchant_key,
            "display_name": self.display_name,
            "avg_amount": float(self.avg_amount),
            "cadence_guess": self.cadence_guess,
            "confidence": self.confidence,
            "last_seen": self.last_seen.isoformat(),
            "next_predicted": self.next_predicted.isoformat(),
            "status": self.status,
            "confirmed_subscription_id": self.confirmed_subscription_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
