from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from .models import GVPStatus, PayoutStatus

class UserCreate(BaseModel):
    name: str
    upi_id: str
    phone_number: str

class UserResponse(UserCreate):
    id: UUID
    wallet_balance: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class GVPResponse(BaseModel):
    id: UUID
    reporter_id: UUID
    latitude: float
    longitude: float
    before_image_url: str
    after_image_url: Optional[str] = None
    ml_confidence_score: float
    status: GVPStatus
    tender_amount: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class GVPReportResponse(BaseModel):
    message: str
    gvp: Optional[GVPResponse] = None
    ml_confidence_score: float

class PayoutResponse(BaseModel):
    id: UUID
    user_id: UUID
    gvp_id: UUID
    amount: float
    status: PayoutStatus
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
