from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.agent_service import AgentService
from app.schemas.agent import (
    Agent, AgentCreateInvite, AgentInviteResponse, 
    AgentRegister, AgentRegisterResponse, AgentHeartbeat, AgentPoll, AgentHeartbeatPayload
)
from app.schemas.task import TaskResponse
from app.schemas.common import OkResponse
from app.api.deps import get_current_user
from app.api.deps_agent import get_current_agent
from app.models.user import User
from app.models.agent import Agent as AgentModel

router = APIRouter()

# Admin Endpoints

@router.get("/", response_model=List[Agent])
async def get_agents(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    # Need to implement get_all in AgentService or use Repo directly
    # For now using repo directly via service wrapper if it existed, or just repo
    from app.repositories.agent import AgentRepository
    repo = AgentRepository(session)
    return await repo.get_all()

@router.post("/create_invite", response_model=AgentInviteResponse)
async def create_invite(
    invite_in: AgentCreateInvite,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    service = AgentService(session)
    secret = await service.create_invite(invite_in)
    return AgentInviteResponse(name=invite_in.name, secret=secret)

@router.delete("/{agent_id}", response_model=OkResponse)
async def delete_agent(
    agent_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    service = AgentService(session)
    success = await service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return OkResponse()

# Agent Side Endpoints

@router.post("/register", response_model=AgentRegisterResponse)
async def register_agent(
    register_in: AgentRegister,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    service = AgentService(session)
    result = await service.register_agent(register_in)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid registration")
    
    agent_id, agent_token = result
    return AgentRegisterResponse(agent_id=agent_id, agent_token=agent_token)

@router.post("/heartbeat", response_model=OkResponse)
async def heartbeat(
    heartbeat_in: AgentHeartbeatPayload,
    request: Request,
    agent: Annotated[AgentModel, Depends(get_current_agent)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    service = AgentService(session)
    await service.heartbeat(agent, ip=request.client.host, cpu=heartbeat_in.cpu, mem=heartbeat_in.mem)
    return OkResponse()

@router.get("/tasks", response_model=List[TaskResponse])
async def poll_tasks(
    agent: Annotated[AgentModel, Depends(get_current_agent)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    service = AgentService(session)
    tasks = await service.get_tasks(agent.id)
    return [TaskResponse.model_validate(t) for t in tasks]
