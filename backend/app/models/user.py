#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

import bcrypt
from datetime import datetime
from .. import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Unique email used for authentication
    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Hashed password storage
    password_hash = db.Column(
        db.LargeBinary(60),
        nullable=False
    )

    # Account creation timestamp
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships to user-owned resources
    subscriptions = db.relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    imports = db.relationship(
        "TransactionImport",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    candidates = db.relationship(
        "RecurringCandidate",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    transactions = db.relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        """Hash and store a new password."""
        if not raw_password or len(raw_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            raw_password.encode("utf-8"),
            salt
        )

    def check_password(self, raw_password: str) -> bool:
        """Verify a password against the stored hash."""
        if not raw_password:
            return False

        try:
            return bcrypt.checkpw(
                raw_password.encode("utf-8"),
                self.password_hash
            )
        except Exception:
            return False
