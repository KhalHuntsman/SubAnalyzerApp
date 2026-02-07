#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

import csv
import io
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import db
from ..models.transaction import TransactionImport, Transaction
from ..models.candidate import RecurringCandidate
from ..utils.normalize import normalize_merchant
from ..utils.recurrence import detect_recurring


# Blueprint for CSV import routes
bp = Blueprint("imports", __name__)


def _parse_date(value: str):
    """Parse a date in YYYY-MM-DD or MM/DD/YYYY format."""
    value = (value or "").strip()

    if not value:
        raise ValueError("Missing date")

    # Some exports include timestamps; keep only date-like portion if present
    # e.g. "02/05/2026 00:00:00" -> "02/05/2026"
    value = value.split()[0].strip()

    try:
        if "-" in value:
            return datetime.fromisoformat(value).date()
        return datetime.strptime(value, "%m/%d/%Y").date()
    except Exception:
        raise ValueError(f"Invalid date: {value}")


def _parse_float(value):
    """Parse a numeric string into float. Supports $ and commas and parentheses."""
    if value is None:
        return None

    s = str(value).strip()
    if not s:
        return None

    s = s.replace("$", "").replace(",", "").strip()

    # Handle accounting format: (15.99)
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]

    try:
        return float(s)
    except Exception:
        return None


def _parse_amount_generic(value: str):
    """Parse a transaction amount and return a positive float."""
    amt = _parse_float(value)
    if amt is None:
        raise ValueError(f"Invalid amount: {value}")

    if amt == 0:
        raise ValueError("Amount cannot be 0")

    return round(abs(amt), 2)


def _clean_csv_text(raw_text: str) -> str:
    """
    Some bank CSVs include metadata lines before the actual header.
    Strip leading lines until a header containing 'date' and an amount column is found.
    """
    lines = [ln.strip("\ufeff").rstrip() for ln in raw_text.splitlines()]

    header_idx = None
    for i, ln in enumerate(lines):
        if not ln or "," not in ln:
            continue

        lowered = ln.lower()
        has_date = "date" in lowered
        has_amount = ("amount" in lowered) or ("amount debit" in lowered) or ("amount credit" in lowered)

        if has_date and has_amount:
            header_idx = i
            break

    if header_idx is None:
        return raw_text

    return "\n".join(lines[header_idx:])


@bp.post("")
@jwt_required()
def upload_csv():
    """Accept a CSV upload, save transactions, and generate recurring candidates."""
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({
            "error": "Missing file. Use multipart/form-data with field name 'file'."
        }), 400

    f = request.files["file"]

    if not f.filename:
        return jsonify({"error": "File must have a filename."}), 400

    content_raw = f.read().decode("utf-8", errors="ignore")
    content = _clean_csv_text(content_raw)

    reader = csv.DictReader(io.StringIO(content))

    # Support common CSV headers (case-insensitive)
    date_keys = {"date", "transaction_date", "posted_date"}

    # For banks like yours, Memo often contains the real merchant. Fall back to Description.
    merchant_keys = {"merchant", "memo", "description", "name"}

    # Traditional single amount column
    amount_keys = {"amount", "transaction_amount"}

    # Split debit/credit exports
    debit_keys = {"amount debit", "debit", "withdrawal", "debits"}
    credit_keys = {"amount credit", "credit", "deposit", "credits"}

    import_record = TransactionImport(
        user_id=user_id,
        filename=f.filename
    )

    db.session.add(import_record)
    db.session.flush()

    rows_added = 0
    rows_skipped = 0

    by_merchant = {}
    display_names = {}

    for row in reader:
        # Map normalized key -> original key in the CSV row
        keys = {(k or "").lower().strip(): k for k in row.keys() if k}

        def pick(options):
            for opt in options:
                if opt in keys:
                    return row.get(keys[opt])
            return None

        date_val = pick(date_keys)
        merch_val = pick(merchant_keys)

        # Amount handling: prefer a single amount column; otherwise use debit/credit
        amt_val = pick(amount_keys)
        debit_val = pick(debit_keys)
        credit_val = pick(credit_keys)

        if not date_val or not merch_val:
            rows_skipped += 1
            continue

        # Decide the amount and whether it should be treated as a "charge"
        # - Debit = spending (use absolute value)
        # - Credit = income/refund; skip for recurring charge detection
        try:
            txn_date = _parse_date(date_val)

            amount = None
            include_in_detection = True

            if amt_val is not None and str(amt_val).strip():
                amount = _parse_amount_generic(amt_val)
            else:
                debit_amt = _parse_float(debit_val)
                credit_amt = _parse_float(credit_val)

                if debit_amt is not None and debit_amt != 0:
                    amount = round(abs(debit_amt), 2)
                elif credit_amt is not None and credit_amt != 0:
                    # Save the transaction, but don't treat credits as recurring "charges"
                    amount = round(abs(credit_amt), 2)
                    include_in_detection = False
                else:
                    raise ValueError("Missing amount")

            merchant_raw = str(merch_val).strip()
            if not merchant_raw:
                raise ValueError("Missing merchant")

            merchant_key = normalize_merchant(merchant_raw)

        except Exception:
            rows_skipped += 1
            continue

        txn = Transaction(
            user_id=user_id,
            import_id=import_record.id,
            txn_date=txn_date,
            merchant_raw=merchant_raw[:255],
            merchant_key=merchant_key,
            amount=amount,
        )

        db.session.add(txn)
        rows_added += 1

        if include_in_detection:
            by_merchant.setdefault(merchant_key, []).append((txn_date, amount))
            display_names.setdefault(merchant_key, merchant_raw)

    db.session.flush()

    candidates_created = 0
    candidates_updated = 0

    for merchant_key, charges in by_merchant.items():
        display_name = display_names.get(merchant_key, merchant_key)

        result = detect_recurring(
            merchant_key,
            display_name,
            charges
        )

        if not result:
            continue

        existing = RecurringCandidate.query.filter_by(
            user_id=user_id,
            merchant_key=result.merchant_key,
            status="pending"
        ).first()

        if existing:
            existing.display_name = result.display_name[:160]
            existing.avg_amount = result.avg_amount
            existing.cadence_guess = result.cadence_guess
            existing.confidence = result.confidence
            existing.last_seen = result.last_seen
            existing.next_predicted = result.next_predicted
            candidates_updated += 1
        else:
            cand = RecurringCandidate(
                user_id=user_id,
                merchant_key=result.merchant_key,
                display_name=result.display_name[:160],
                avg_amount=result.avg_amount,
                cadence_guess=result.cadence_guess,
                confidence=result.confidence,
                last_seen=result.last_seen,
                next_predicted=result.next_predicted,
                status="pending",
            )
            db.session.add(cand)
            candidates_created += 1

    db.session.commit()

    return jsonify({
        "import": import_record.to_dict(),
        "rows_added": rows_added,
        "rows_skipped": rows_skipped,
        "candidates_created": candidates_created,
        "candidates_updated": candidates_updated,
    }), 201
