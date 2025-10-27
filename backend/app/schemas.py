"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction via webhook."""

    source: str = Field(..., description="Payment source: rakuten_card, paypay, suica, japan_post")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    vendor: str = Field(..., description="Vendor/merchant name")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="JPY", description="Currency code")
    payment_method: str = Field(..., description="Payment method type")
    raw_text: Optional[str] = Field(None, description="Raw notification/email text")

    @validator('source')
    def validate_source(cls, v):
        allowed_sources = ['rakuten_card', 'paypay', 'suica', 'japan_post']
        if v not in allowed_sources:
            raise ValueError(f'source must be one of {allowed_sources}')
        return v

    @validator('payment_method')
    def validate_payment_method(cls, v):
        allowed_methods = ['credit_card', 'mobile_payment', 'transit_card', 'bank_transfer']
        if v not in allowed_methods:
            raise ValueError(f'payment_method must be one of {allowed_methods}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "source": "rakuten_card",
                "timestamp": "2025-10-27T14:30:00+09:00",
                "vendor": "Family Mart",
                "amount": 1250,
                "currency": "JPY",
                "payment_method": "credit_card",
                "raw_text": "ご利用ありがとうございます。Family Martで1,250円のお支払いがありました。"
            }
        }


class TransactionResponse(BaseModel):
    """Schema for transaction response."""

    id: int
    source: str
    timestamp: datetime
    vendor: str
    amount: float
    currency: str
    payment_method: str
    category: Optional[str] = None
    transaction_hash: str
    is_duplicate: bool
    raw_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    """Schema for creating a category."""

    name: str = Field(..., description="Internal category name (lowercase_underscore)")
    display_name: str = Field(..., description="Display name for UI")
    color: Optional[str] = Field(None, description="Hex color code")
    icon: Optional[str] = Field(None, description="Icon emoji or name")
    budget_limit: Optional[float] = Field(None, description="Monthly budget limit")


class CategoryResponse(BaseModel):
    """Schema for category response."""

    id: int
    name: str
    display_name: str
    color: Optional[str] = None
    icon: Optional[str] = None
    budget_limit: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    """Schema for creating a goal."""

    name: str = Field(..., description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    target_amount: float = Field(..., gt=0, description="Target amount")
    deadline: Optional[datetime] = Field(None, description="Goal deadline")


class GoalResponse(BaseModel):
    """Schema for goal response."""

    id: int
    name: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float
    deadline: Optional[datetime] = None
    is_active: bool
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    """Schema for creating an alert."""

    name: str = Field(..., description="Alert name")
    alert_type: str = Field(..., description="Alert type: daily_limit, category_limit, monthly_limit")
    threshold_amount: float = Field(..., gt=0, description="Threshold amount")
    category: Optional[str] = Field(None, description="Category (for category_limit type)")

    @validator('alert_type')
    def validate_alert_type(cls, v):
        allowed_types = ['daily_limit', 'category_limit', 'monthly_limit']
        if v not in allowed_types:
            raise ValueError(f'alert_type must be one of {allowed_types}')
        return v


class AlertResponse(BaseModel):
    """Schema for alert response."""

    id: int
    name: str
    alert_type: str
    threshold_amount: float
    category: Optional[str] = None
    is_active: bool
    last_triggered: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookResponse(BaseModel):
    """Schema for webhook response."""

    status: str
    message: str
    transaction_id: Optional[int] = None
    is_duplicate: bool = False
