from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.enums import AllocationStatus

class AllocationBase(BaseModel):
    service: str = "code_server"

class AllocationCreate(AllocationBase):
    agent_id: int

class AllocationResponse(AllocationBase):
    id: int
    agent_id: int
    remote_port: int
    status: AllocationStatus
    access_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AllocationRelease(BaseModel):
    pass
