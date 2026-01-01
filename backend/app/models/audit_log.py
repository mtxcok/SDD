from sqlalchemy import Column, Integer, String, DateTime, func, Enum, JSON
from app.models.base import Base
from app.models.enums import ActorType

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_type = Column(Enum(ActorType), nullable=False)
    actor_id = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=True)
    target_id = Column(Integer, nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
