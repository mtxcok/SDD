from sqlalchemy import Column, Integer, String, DateTime, func, Enum, Float
from app.models.base import Base
from app.models.enums import AgentStatus

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    secret_hash = Column(String(255), nullable=False)
    agent_token_hash = Column(String(255), nullable=True)
    ip = Column(String(50), nullable=True)
    cpu = Column(Float, nullable=True)
    mem = Column(Float, nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(AgentStatus), default=AgentStatus.OFFLINE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
