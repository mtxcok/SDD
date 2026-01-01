from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.task import TaskReport
from app.models.enums import TaskStatus
from app.repositories.task import TaskRepository

router = APIRouter()

@router.post("/{id}/report", response_model=dict)
async def report_task(
    id: int,
    report_in: TaskReport,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    # Note: In a real app, we should verify the agent calling this owns the task
    repo = TaskRepository(session)
    task = await repo.get(id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = TaskStatus.DONE if report_in.status == "done" else TaskStatus.FAILED
    await repo.update(task, {
        "status": status,
        "last_error": report_in.message
    })
    
    # If task was start_code_server and done, update allocation status to ACTIVE
    # If task was stop_code_server and done, update allocation status to RELEASED
    # This logic should ideally be in a service or event handler
    if task.type == "start_code_server" and status == TaskStatus.DONE:
        from app.repositories.allocation import AllocationRepository
        from app.models.enums import AllocationStatus
        alloc_repo = AllocationRepository(session)
        # Extract allocation_id from payload
        alloc_id = task.payload.get("allocation_id")
        if alloc_id:
            alloc = await alloc_repo.get(alloc_id)
            if alloc:
                await alloc_repo.update(alloc, {"status": AllocationStatus.ACTIVE})

    elif task.type == "stop_code_server" and status == TaskStatus.DONE:
        from app.repositories.allocation import AllocationRepository
        from app.models.enums import AllocationStatus
        alloc_repo = AllocationRepository(session)
        alloc_id = task.payload.get("allocation_id")
        if alloc_id:
            alloc = await alloc_repo.get(alloc_id)
            if alloc:
                await alloc_repo.update(alloc, {"status": AllocationStatus.RELEASED, "released_at": task.updated_at})

    return {"ok": True}
