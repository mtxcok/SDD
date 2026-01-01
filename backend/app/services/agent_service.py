import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.agent import AgentRepository
from app.repositories.task import TaskRepository
from app.schemas.agent import AgentCreateInvite, AgentRegister
from app.core.security import get_password_hash, verify_password
from app.models.agent import Agent
from app.models.enums import AgentStatus
from datetime import datetime

class AgentService:
    def __init__(self, session: AsyncSession):
        self.agent_repo = AgentRepository(session)
        self.task_repo = TaskRepository(session)

    async def create_invite(self, invite_in: AgentCreateInvite) -> str:
        # Generate a random secret
        secret = secrets.token_urlsafe(32)
        secret_hash = get_password_hash(secret)
        
        await self.agent_repo.create({
            "name": invite_in.name,
            "secret_hash": secret_hash,
            "status": AgentStatus.OFFLINE
        })
        return secret

    async def register_agent(self, register_in: AgentRegister) -> tuple[int, str] | None:
        agent = await self.agent_repo.get_by_name(register_in.name)
        if not agent:
            return None
        
        if not verify_password(register_in.secret, agent.secret_hash):
            return None
            
        # Generate agent token
        agent_token = secrets.token_urlsafe(32)
        agent_token_hash = get_password_hash(agent_token)
        
        await self.agent_repo.update(agent, {
            "agent_token_hash": agent_token_hash,
            "status": AgentStatus.ONLINE,
            "last_seen_at": datetime.utcnow()
        })
        
        return agent.id, agent_token

    async def authenticate_agent(self, agent_id: int, agent_token: str) -> Agent | None:
        agent = await self.agent_repo.get(agent_id)
        if not agent:
            return None
        
        # In a real scenario, we might want to cache this or optimize
        if not agent.agent_token_hash or not verify_password(agent_token, agent.agent_token_hash):
            return None
            
        return agent

    async def heartbeat(self, agent: Agent, ip: str = None):
        await self.agent_repo.update(agent, {
            "last_seen_at": datetime.utcnow(),
            "status": AgentStatus.ONLINE,
            "ip": ip
        })

    async def get_tasks(self, agent_id: int):
        return await self.task_repo.get_pending_tasks(agent_id)
