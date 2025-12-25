"""Database models"""

from sqlalchemy import Column, String, Text, TIMESTAMP, JSON
from sqlalchemy.sql import func
import uuid
from ..database import Base

class SynthesisReport(Base):
    __tablename__ = "synthesis_reports"
    
    # Using String for UUID to support both SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_type = Column(String(50), nullable=False, index=True)  # patient_summary, comparison
    # Using JSON instead of JSONB for SQLite compatibility
    patient_ids = Column(JSON)  # Array of patient IDs
    synthesis_text = Column(Text, nullable=False)
    key_findings = Column(JSON)
    llm_model = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

