#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from datetime import datetime
from .. import db


# Allowed billing cadence values
ALLOWED_CADENCES = {"weekly", "monthly", "quarterly", "yearly"}


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking this subscription to a user
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # User-facing subscription name
    name = db.Column(
        db.String(120),
        nullable=False
    )

    # Normalized merchant identifier for grouping
    merchant_key = db.Column(
        db.String(160),
        nullable=False,
        index=True
    )

    # Recurring payment amount
    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    # Billing cadence (weekly/monthly/etc.)
    cadence = db.Column(
        db.String(20),
        nullable=False
    )

    # Next expected charge date
    next_due_date = db.Column(
        db.Date,
        nullable=False
    )

    # Optional categorization
    category = db.Column(
        db.String(60),
        nullable=True
    )

    # Active or canceled status
    status = db.Column(
        db.String(20),
        nullable=False,
        default="active"
    )

    # Optional user notes
    notes = db.Column(
        db.Text,
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
        back_populates="subscriptions"
    )

    def to_dict(self):
        """Convert model instance to a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "merchant_key": self.merchant_key,
            "amount": float(self.amount),
            "cadence": self.cadence,
            "next_due_date": self.next_due_date.isoformat(),
            "category": self.category,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
