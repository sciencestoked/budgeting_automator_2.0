"""SQLAlchemy database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Transaction(Base):
    """Transaction model for storing expense records."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # Transaction details
    source = Column(String, nullable=False)  # rakuten_card, paypay, suica, japan_post
    timestamp = Column(DateTime, nullable=False, index=True)
    vendor = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="JPY")
    payment_method = Column(String)  # credit_card, mobile_payment, transit_card, bank_transfer

    # Categorization
    category = Column(String, index=True)  # food_snack, utilities, shopping, transport, etc.

    # Deduplication
    transaction_hash = Column(String, unique=True, index=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_count = Column(Integer, default=0)

    # Raw data for debugging
    raw_text = Column(String)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction(id={self.id}, vendor='{self.vendor}', amount={self.amount}, category='{self.category}')>"


class Category(Base):
    """Category model for organizing transactions."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    color = Column(String)  # Hex color for UI
    icon = Column(String)  # Icon name/emoji
    budget_limit = Column(Float)  # Monthly budget limit

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Goal(Base):
    """Goal model for tracking savings/spending goals."""

    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    # Goal details
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Goal(id={self.id}, name='{self.name}', progress={self.current_amount}/{self.target_amount})>"


class Alert(Base):
    """Alert model for budget threshold notifications."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)  # daily_limit, category_limit, monthly_limit

    # Alert configuration
    threshold_amount = Column(Float, nullable=False)
    category = Column(String)  # Optional: specific category

    # Status
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Alert(id={self.id}, name='{self.name}', threshold={self.threshold_amount})>"


class RawDataDump(Base):
    """Model for storing raw data from shortcuts for analysis."""

    __tablename__ = "raw_data_dumps"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False, index=True)  # email, notification, screenshot, manual
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(String)  # The full text content
    metadata_json = Column(String)  # JSON string for additional metadata

    # Analysis flags
    analyzed = Column(Boolean, default=False)
    extraction_successful = Column(Boolean)
    notes = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RawDataDump(id={self.id}, source='{self.source}', analyzed={self.analyzed})>"


class PendingClarification(Base):
    """Model for transactions needing user review."""

    __tablename__ = "pending_clarifications"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    issue_type = Column(String, nullable=False)  # 'category', 'duplicate', 'vendor', 'missing_data'
    confidence_score = Column(Float)
    description = Column(String)

    # For potential duplicates
    potential_duplicate_id = Column(Integer, ForeignKey('transactions.id'))

    # Resolution
    resolved = Column(Boolean, default=False)
    user_action = Column(String)  # 'confirm', 'ignore', 'merge', 'recategorize', 'edit_vendor'
    resolved_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PendingClarification(id={self.id}, type='{self.issue_type}', resolved={self.resolved})>"
