"""
Database models for the application.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, 
    Integer, String, Text, func, text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.core import Base


class Analysis(Base):
    """Analysis model for storing proposal analysis results."""
    
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    proposal_id = Column(String(255), nullable=False, index=True)
    result = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    details = Column(Text, nullable=False)
    arguments = Column(JSONB, nullable=True)  # Store arguments in JSONB format
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, proposal_id={self.proposal_id}, result={self.result})>"


class WebhookEvent(Base):
    """Webhook event model for storing incoming webhook events."""
    
    __tablename__ = "webhook_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    event_type = Column(String(100), nullable=False)
    proposal_data = Column(JSONB, nullable=False)
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, event_type={self.event_type}, processed={self.processed})>"
