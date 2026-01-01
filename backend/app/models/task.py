from sqlalchemy import Column, Integer, String, DateTime, func, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.enums import TaskStatus

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_error = Column(String(255), nullable=True)

    agent = relationship("Agent")
