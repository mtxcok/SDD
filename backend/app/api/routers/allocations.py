from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.allocation_service import AllocationService
from app.schemas.allocation import AllocationCreate, AllocationResponse, AllocationRelease
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/create", response_model=AllocationResponse)
async def create_allocation(
    alloc_in: AllocationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    service = AllocationService(session)
    try:
        allocation = await service.allocate_port(alloc_in.agent_id, alloc_in.service)
        return allocation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/release", response_model=dict)
async def release_allocation(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    service = AllocationService(session)
    await service.release_allocation(id)
    return {"ok": True}

@router.get("/", response_model=List[AllocationResponse])
async def get_allocations(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    agent_id: int | None = None
):
    from app.repositories.allocation import AllocationRepository
    repo = AllocationRepository(session)
    if agent_id:
        return await repo.get_by_agent(agent_id)
    return await repo.get_all()
