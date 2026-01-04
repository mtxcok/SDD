import random
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.allocation import AllocationRepository
from app.repositories.task import TaskRepository
from app.core.config import settings
from app.core.redis import redis_client
from app.models.enums import AllocationStatus, TaskStatus, ActorType
from app.models.allocation import Allocation
from app.services.audit_service import AuditService

class AllocationService:
    def __init__(self, session: AsyncSession):
        self.alloc_repo = AllocationRepository(session)
        self.task_repo = TaskRepository(session)
        self.audit_service = AuditService(session)

    async def allocate_port(self, agent_id: int, user_id: int, service: str = "code_server") -> Allocation:
        # 1. Acquire Redis Lock
        try:
            lock = redis_client.lock("port_alloc_lock", timeout=5)
            acquired = await lock.acquire(blocking=True)
            if not acquired:
                 raise Exception("Could not acquire lock")
        except Exception as e:
             # Fallback if redis is not available or lock fails, though in prod we should handle this better
             print(f"Warning: Redis lock failed: {e}")
             # Proceeding without lock for now to debug logic, or re-raise
             # raise e 
             pass

        try:
            # 2. Get used ports
            used_ports = await self.alloc_repo.get_active_ports()
            used_ports_set = set(used_ports)
            
            # 3. Find free port
            # Simple random strategy with retry or linear scan
            # For range 50000-60000 (10000 ports), random is fine usually, but linear scan is safer for fullness
            
            available_port = None
            # Try random first for speed
            for _ in range(10):
                p = random.randint(settings.PORT_MIN, settings.PORT_MAX)
                if p not in used_ports_set:
                    available_port = p
                    break
            
            # If random failed, linear scan
            if available_port is None:
                for p in range(settings.PORT_MIN, settings.PORT_MAX + 1):
                    if p not in used_ports_set:
                        available_port = p
                        break
            
            if available_port is None:
                raise Exception("No available ports")

            # 4. Create Allocation
            allocation = await self.alloc_repo.create({
                "agent_id": agent_id,
                "user_id": user_id,
                "service": service,
                "remote_port": available_port,
                "status": AllocationStatus.REQUESTED
            })
        finally:
            try:
                if 'lock' in locals() and await lock.locked():
                    await lock.release()
            except Exception:
                pass

        # 5. Create Task for Agent (outside lock)
        # Payload: remote_port, cs_password (generated)
        cs_password = "password123" # Should be random
        
        await self.task_repo.create({
            "agent_id": agent_id,
            "type": "start_code_server",
            "payload": {
                "allocation_id": allocation.id,
                "remote_port": available_port,
                "password": cs_password
            },
            "status": TaskStatus.PENDING
        })
        
        # Audit Log
        await self.audit_service.record_log(
            actor_type=ActorType.SYSTEM, # Or USER if we passed current_user
            actor_id=0, # System
            action="create_allocation",
            target_type="allocation",
            target_id=allocation.id,
            meta={"agent_id": agent_id, "port": available_port}
        )

        return allocation

    async def release_allocation(self, allocation_id: int):
        allocation = await self.alloc_repo.get(allocation_id)
        if not allocation:
            return
            
        await self.alloc_repo.update(allocation, {"status": AllocationStatus.RELEASING})
        
        # Create Task
        await self.task_repo.create({
            "agent_id": allocation.agent_id,
            "type": "stop_code_server",
            "payload": {
                "allocation_id": allocation.id,
                "remote_port": allocation.remote_port
            },
            "status": TaskStatus.PENDING
        })

        # Audit Log
        await self.audit_service.record_log(
            actor_type=ActorType.SYSTEM,
            actor_id=0,
            action="release_allocation",
            target_type="allocation",
            target_id=allocation.id
        )
