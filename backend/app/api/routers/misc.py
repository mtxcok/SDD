from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.schemas.common import HealthResponse, PortsAvailableResponse
from app.repositories.allocation import AllocationRepository

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")

@router.get("/ports/available", response_model=PortsAvailableResponse)
async def get_available_ports(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    repo = AllocationRepository(session)
    active_ports = await repo.get_active_ports()
    allocated_count = len(active_ports)
    
    return PortsAvailableResponse(
        min=settings.PORT_MIN,
        max=settings.PORT_MAX,
        allocated_count=allocated_count
    )
