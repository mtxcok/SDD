from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.agent_service import AgentService
from app.models.agent import Agent

# We use OAuth2PasswordBearer to extract the Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/agents/register", auto_error=False)

async def get_current_agent(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> Agent:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception

    try:
        # Expect token format: "agent_id:raw_token"
        # This allows us to look up the agent by ID and then verify the hash
        if ":" not in token:
             raise credentials_exception
        
        agent_id_str, raw_token = token.split(":", 1)
        if not agent_id_str.isdigit():
            raise credentials_exception
            
        agent_id = int(agent_id_str)
    except ValueError:
        raise credentials_exception

    service = AgentService(session)
    agent = await service.authenticate_agent(agent_id, raw_token)
    if not agent:
        raise credentials_exception
    
    return agent
