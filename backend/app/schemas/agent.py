from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.enums import AgentStatus, TaskStatus

# Shared properties
class AgentBase(BaseModel):
    name: str

# Properties to receive on item creation
class AgentCreateInvite(AgentBase):
    pass

class AgentInviteResponse(AgentBase):
    secret: str

class AgentRegister(AgentBase):
    secret: str

class AgentRegisterResponse(BaseModel):
    agent_id: int
    agent_token: str

class AgentHeartbeatPayload(BaseModel):
    cpu: Optional[float] = None
    mem: Optional[float] = None

class AgentHeartbeat(BaseModel):
    agent_id: int
    agent_token: str
    cpu: Optional[float] = None
    mem: Optional[float] = None
    ip: Optional[str] = None

class AgentPoll(BaseModel):
    agent_id: int
    agent_token: str

class Agent(AgentBase):
    id: int
    status: AgentStatus
    last_seen_at: Optional[datetime]
    ip: Optional[str]
    # active_allocations: List[Allocation] # Circular dependency, handle later if needed

    class Config:
        from_attributes = True
