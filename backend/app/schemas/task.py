from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict
from app.models.enums import TaskStatus

class TaskBase(BaseModel):
    type: str
    payload: Optional[Dict[str, Any]] = None

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime

    class Config:
        from_attributes = True

class TaskReport(BaseModel):
    status: str # "done" | "failed"
    message: Optional[str] = None
