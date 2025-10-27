"""CRUD operations for database models."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, schemas
from .deduplication import generate_transaction_hash
from .categorization import categorize_transaction


def create_transaction(db: Session, transaction: schemas.TransactionCreate) -> models.Transaction:
    """
    Create a new transaction with deduplication and auto-categorization.

    Args:
        db: Database session
        transaction: Transaction data from webhook

    Returns:
        Created transaction object
    """
    # Generate transaction hash
    tx_hash = generate_transaction_hash(
        vendor=transaction.vendor,
        amount=transaction.amount,
        timestamp=transaction.timestamp,
        source=transaction.source
    )

    # Check for duplicate
    existing = db.query(models.Transaction).filter(
        models.Transaction.transaction_hash == tx_hash
    ).first()

    if existing:
        # Update duplicate count
        existing.duplicate_count += 1
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)

        # Return existing with duplicate flag
        existing.is_duplicate = True
        return existing

    # Auto-categorize
    category = categorize_transaction(transaction.vendor)

    # Create new transaction
    db_transaction = models.Transaction(
        source=transaction.source,
        timestamp=transaction.timestamp,
        vendor=transaction.vendor,
        amount=transaction.amount,
        currency=transaction.currency,
        payment_method=transaction.payment_method,
        category=category,
        transaction_hash=tx_hash,
        is_duplicate=False,
        duplicate_count=0,
        raw_text=transaction.raw_text
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[models.Transaction]:
    """
    Get transactions with optional filters.

    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        category: Filter by category
        start_date: Filter by start date
        end_date: Filter by end date

    Returns:
        List of transactions
    """
    query = db.query(models.Transaction).filter(
        models.Transaction.is_duplicate == False
    )

    if category:
        query = query.filter(models.Transaction.category == category)

    if start_date:
        query = query.filter(models.Transaction.timestamp >= start_date)

    if end_date:
        query = query.filter(models.Transaction.timestamp <= end_date)

    return query.order_by(models.Transaction.timestamp.desc()).offset(skip).limit(limit).all()


def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    """Get a specific transaction by ID."""
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()


def get_total_spent(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None
) -> float:
    """
    Calculate total amount spent in a date range.

    Args:
        db: Database session
        start_date: Start date for calculation
        end_date: End date for calculation
        category: Filter by category

    Returns:
        Total amount spent
    """
    query = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.is_duplicate == False
    )

    if start_date:
        query = query.filter(models.Transaction.timestamp >= start_date)

    if end_date:
        query = query.filter(models.Transaction.timestamp <= end_date)

    if category:
        query = query.filter(models.Transaction.category == category)

    result = query.scalar()
    return result if result else 0.0


def get_category_breakdown(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> dict:
    """
    Get spending breakdown by category.

    Args:
        db: Database session
        start_date: Start date for calculation
        end_date: End date for calculation

    Returns:
        Dictionary mapping category to total amount
    """
    query = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label('total')
    ).filter(
        models.Transaction.is_duplicate == False
    )

    if start_date:
        query = query.filter(models.Transaction.timestamp >= start_date)

    if end_date:
        query = query.filter(models.Transaction.timestamp <= end_date)

    results = query.group_by(models.Transaction.category).all()

    return {category: float(total) for category, total in results}


# Category CRUD operations
def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """Create a new category."""
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_categories(db: Session) -> List[models.Category]:
    """Get all categories."""
    return db.query(models.Category).all()


# Goal CRUD operations
def create_goal(db: Session, goal: schemas.GoalCreate) -> models.Goal:
    """Create a new goal."""
    db_goal = models.Goal(**goal.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_goals(db: Session, active_only: bool = True) -> List[models.Goal]:
    """Get goals."""
    query = db.query(models.Goal)
    if active_only:
        query = query.filter(models.Goal.is_active == True)
    return query.all()


# Alert CRUD operations
def create_alert(db: Session, alert: schemas.AlertCreate) -> models.Alert:
    """Create a new alert."""
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_alerts(db: Session, active_only: bool = True) -> List[models.Alert]:
    """Get alerts."""
    query = db.query(models.Alert)
    if active_only:
        query = query.filter(models.Alert.is_active == True)
    return query.all()
