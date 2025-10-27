"""FastAPI main application."""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import models, schemas, crud
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Budget Automation API",
    description="API for automated budget tracking and expense management",
    version="1.0.0"
)

# Add CORS middleware (for web dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint - API status."""
    return {
        "status": "online",
        "message": "Budget Automation API v1.0.0",
        "endpoints": {
            "docs": "/docs",
            "webhook": "/api/webhook",
            "transactions": "/api/transactions"
        }
    }


@app.post("/api/webhook", response_model=schemas.WebhookResponse)
def receive_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint to receive transaction data from Apple Shortcuts.

    This endpoint:
    1. Validates the incoming JSON
    2. Checks for duplicates
    3. Auto-categorizes the transaction
    4. Stores in database
    """
    try:
        db_transaction = crud.create_transaction(db=db, transaction=transaction)

        if db_transaction.is_duplicate:
            return schemas.WebhookResponse(
                status="duplicate",
                message=f"Duplicate transaction detected for {transaction.vendor}",
                transaction_id=db_transaction.id,
                is_duplicate=True
            )

        return schemas.WebhookResponse(
            status="success",
            message=f"Transaction recorded: {transaction.vendor} - ¥{transaction.amount}",
            transaction_id=db_transaction.id,
            is_duplicate=False
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get transactions with optional filters.

    Query parameters:
    - skip: Pagination offset (default: 0)
    - limit: Number of records (default: 100)
    - category: Filter by category
    - start_date: Filter by start date (ISO format)
    - end_date: Filter by end date (ISO format)
    """
    transactions = crud.get_transactions(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        start_date=start_date,
        end_date=end_date
    )
    return transactions


@app.get("/api/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get a specific transaction by ID."""
    transaction = crud.get_transaction_by_id(db=db, transaction_id=transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.get("/api/summary")
def get_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get spending summary for a date range.

    Returns:
    - total: Total amount spent
    - by_category: Breakdown by category
    - transaction_count: Number of transactions
    """
    total = crud.get_total_spent(db=db, start_date=start_date, end_date=end_date)
    by_category = crud.get_category_breakdown(db=db, start_date=start_date, end_date=end_date)

    # Count transactions
    transactions = crud.get_transactions(
        db=db,
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )

    return {
        "total": total,
        "by_category": by_category,
        "transaction_count": len(transactions),
        "date_range": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None
        }
    }


@app.get("/api/categories", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories."""
    return crud.get_categories(db=db)


@app.post("/api/categories", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    return crud.create_category(db=db, category=category)


@app.get("/api/goals", response_model=List[schemas.GoalResponse])
def get_goals(active_only: bool = True, db: Session = Depends(get_db)):
    """Get goals."""
    return crud.get_goals(db=db, active_only=active_only)


@app.post("/api/goals", response_model=schemas.GoalResponse)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    """Create a new goal."""
    return crud.create_goal(db=db, goal=goal)


@app.get("/api/alerts", response_model=List[schemas.AlertResponse])
def get_alerts(active_only: bool = True, db: Session = Depends(get_db)):
    """Get alerts."""
    return crud.get_alerts(db=db, active_only=active_only)


@app.post("/api/alerts", response_model=schemas.AlertResponse)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert."""
    return crud.create_alert(db=db, alert=alert)


@app.post("/api/data-dump")
def receive_raw_data(data: dict, db: Session = Depends(get_db)):
    """
    Endpoint for collecting raw data from Apple Shortcuts during discovery phase.
    Accepts ANY JSON and stores it for later analysis.

    This helps understand what data we can extract from different sources.
    """
    import json

    raw_dump = models.RawDataDump(
        source=data.get("source", "unknown"),
        raw_text=data.get("raw_text") or data.get("body") or json.dumps(data),
        metadata_json=json.dumps(data),
        analyzed=False
    )

    db.add(raw_dump)
    db.commit()
    db.refresh(raw_dump)

    return {
        "status": "success",
        "message": "Raw data received for analysis",
        "dump_id": raw_dump.id
    }


@app.get("/api/data-dumps")
def get_raw_dumps(
    skip: int = 0,
    limit: int = 50,
    source: Optional[str] = None,
    analyzed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get raw data dumps for analysis."""
    query = db.query(models.RawDataDump)

    if source:
        query = query.filter(models.RawDataDump.source == source)
    if analyzed is not None:
        query = query.filter(models.RawDataDump.analyzed == analyzed)

    dumps = query.order_by(models.RawDataDump.created_at.desc()).offset(skip).limit(limit).all()

    return [{
        "id": d.id,
        "source": d.source,
        "timestamp": d.timestamp,
        "raw_text": d.raw_text,
        "metadata": d.metadata_json,
        "analyzed": d.analyzed,
        "created_at": d.created_at
    } for d in dumps]


@app.get("/api/clarifications")
def get_pending_clarifications(
    resolved: bool = False,
    db: Session = Depends(get_db)
):
    """Get transactions that need user review."""
    clarifications = db.query(models.PendingClarification).filter(
        models.PendingClarification.resolved == resolved
    ).all()

    return [{
        "id": c.id,
        "transaction_id": c.transaction_id,
        "issue_type": c.issue_type,
        "confidence_score": c.confidence_score,
        "description": c.description,
        "potential_duplicate_id": c.potential_duplicate_id,
        "resolved": c.resolved,
        "user_action": c.user_action
    } for c in clarifications]


if __name__ == "__main__":
    import uvicorn
    from .config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
