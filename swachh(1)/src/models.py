import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from src.database import Base
import enum

class GVPStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FUNDED = "FUNDED"
    CLEANED = "CLEANED"
    PAID = "PAID"

class PayoutStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    upi_id = Column(String, unique=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    wallet_balance = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    reported_gvps = relationship("GVP", back_populates="reporter")
    payouts = relationship("Payout", back_populates="user")

class GVP(Base):
    __tablename__ = "gvps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=False) # SRID 4326 = WGS84
    before_image_url = Column(String, nullable=False)
    after_image_url = Column(String, nullable=True)
    ml_confidence_score = Column(Float, nullable=False)
    status = Column(Enum(GVPStatus), default=GVPStatus.PENDING, nullable=False)
    corporate_sponsor_id = Column(UUID(as_uuid=True), nullable=True) # Could be a FK to a Sponsors table
    tender_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    reporter = relationship("User", back_populates="reported_gvps")
    payouts = relationship("Payout", back_populates="gvp")

class Payout(Base):
    __tablename__ = "payouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    gvp_id = Column(UUID(as_uuid=True), ForeignKey("gvps.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    razorpay_fund_account_id = Column(String, nullable=True)
    razorpay_payout_id = Column(String, nullable=True, unique=True)
    status = Column(Enum(PayoutStatus), default=PayoutStatus.PENDING, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="payouts")
    gvp = relationship("GVP", back_populates="payouts")
