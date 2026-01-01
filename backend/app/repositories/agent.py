from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.agent import Agent
from app.repositories.base import BaseRepository

class AgentRepository(BaseRepository[Agent]):
    def __init__(self, session: AsyncSession):
        super().__init__(Agent, session)

    async def get_by_name(self, name: str) -> Agent | None:
        result = await self.session.execute(select(Agent).where(Agent.name == name))
        return result.scalars().first()
