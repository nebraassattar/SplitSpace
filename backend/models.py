"""Database schema. See specifications.md sections 5 and 6."""
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint

db = SQLAlchemy()


def now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)  # stored lowercase
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)


class Household(db.Model):
    __tablename__ = "households"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    invite_code = db.Column(db.String(8), unique=True, nullable=False)
    created_by = db.Column(db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)


class Membership(db.Model):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "household_id"),
        CheckConstraint("role IN ('owner', 'member')"),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    household_id = db.Column(db.ForeignKey("households.id"), nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False, default="member")
    joined_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)


class Expense(db.Model):
    __tablename__ = "expenses"
    __table_args__ = (CheckConstraint("amount_cents > 0"),)
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.ForeignKey("households.id"), nullable=False, index=True)
    payer_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now, nullable=False)
    shares = db.relationship("ExpenseShare", cascade="all, delete-orphan", backref="expense")


class ExpenseShare(db.Model):
    __tablename__ = "expense_shares"
    __table_args__ = (
        UniqueConstraint("expense_id", "user_id"),
        CheckConstraint("share_cents >= 0"),
    )
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    share_cents = db.Column(db.Integer, nullable=False)


class Settlement(db.Model):
    __tablename__ = "settlements"
    __table_args__ = (
        CheckConstraint("amount_cents > 0"),
        CheckConstraint("from_user_id <> to_user_id"),
    )
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.ForeignKey("households.id"), nullable=False, index=True)
    from_user_id = db.Column(db.ForeignKey("users.id"), nullable=False)  # who paid back
    to_user_id = db.Column(db.ForeignKey("users.id"), nullable=False)  # who received it
    amount_cents = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    note = db.Column(db.String(120))
    created_by = db.Column(db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)


class Chore(db.Model):
    __tablename__ = "chores"
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.ForeignKey("households.id"), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    assignee_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True))  # null = open
    created_by = db.Column(db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)
