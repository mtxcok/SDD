from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task
from app.models.enums import TaskStatus
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_pending_tasks(self, agent_id: int) -> List[Task]:
        result = await self.session.execute(
            select(Task).where(
                Task.agent_id == agent_id,
                Task.status == TaskStatus.PENDING
            )
        )
        return result.scalars().all()
