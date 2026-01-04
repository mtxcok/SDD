from sqlalchemy import Column, Integer, String, DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.enums import AllocationStatus

class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # TODO: Make nullable=False after migration
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    service = Column(String(100), nullable=False)
    remote_port = Column(Integer, unique=True, nullable=False)
    status = Column(Enum(AllocationStatus), default=AllocationStatus.REQUESTED)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)
    error_msg = Column(String(255), nullable=True)

    agent = relationship("Agent")
