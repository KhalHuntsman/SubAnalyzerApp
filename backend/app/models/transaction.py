#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

from datetime import datetime
from .. import db


class TransactionImport(db.Model):
    __tablename__ = "transaction_imports"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking this import to a user
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Original filename of the uploaded CSV
    filename = db.Column(
        db.String(255),
        nullable=False
    )

    # Timestamp of when the import occurred
    imported_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship back to the owning user
    user = db.relationship(
        "User",
        back_populates="imports"
    )

    # All transactions associated with this import
    transactions = db.relationship(
        "Transaction",
        back_populates="import_ref",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert model instance to a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "imported_at": self.imported_at.isoformat(),
        }


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking this transaction to a user
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Foreign key linking to the parent import batch
    import_id = db.Column(
        db.Integer,
        db.ForeignKey("transaction_imports.id"),
        nullable=False,
        index=True
    )

    # Date of the transaction
    txn_date = db.Column(
        db.Date,
        nullable=False
    )

    # Raw merchant string from the CSV
    merchant_raw = db.Column(
        db.String(255),
        nullable=False
    )

    # Normalized merchant key used for grouping
    merchant_key = db.Column(
        db.String(160),
        nullable=False,
        index=True
    )

    # Transaction amount
    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    # Timestamp of when this record was created
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship back to the owning user
    user = db.relationship(
        "User",
        back_populates="transactions"
    )

    # Relationship to the import batch
    import_ref = db.relationship(
        "TransactionImport",
        back_populates="transactions"
    )

    def to_dict(self):
        """Convert model instance to a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "import_id": self.import_id,
            "txn_date": self.txn_date.isoformat(),
            "merchant_raw": self.merchant_raw,
            "merchant_key": self.merchant_key,
            "amount": float(self.amount),
            "created_at": self.created_at.isoformat(),
        }
