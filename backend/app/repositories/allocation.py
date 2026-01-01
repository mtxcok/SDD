from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.allocation import Allocation
from app.models.enums import AllocationStatus
from app.repositories.base import BaseRepository

class AllocationRepository(BaseRepository[Allocation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Allocation, session)

    async def get_active_ports(self) -> List[int]:
        result = await self.session.execute(
            select(Allocation.remote_port).where(
                Allocation.status.in_([AllocationStatus.ACTIVE, AllocationStatus.STARTING, AllocationStatus.REQUESTED])
            )
        )
        return result.scalars().all()

    async def get_by_agent(self, agent_id: int) -> List[Allocation]:
        result = await self.session.execute(select(Allocation).where(Allocation.agent_id == agent_id))
        return result.scalars().all()
