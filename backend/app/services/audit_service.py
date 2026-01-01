from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.models.enums import ActorType

class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_log(
        self,
        actor_type: ActorType,
        actor_id: int,
        action: str,
        target_type: str = None,
        target_id: int = None,
        meta: dict = None
    ):
        log = AuditLog(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            meta=meta
        )
        self.session.add(log)
        # We don't commit here, let the caller commit or use a context manager
        # But for simplicity in this architecture, we might want to commit if it's a fire-and-forget log
        # However, usually it's part of the transaction.
        # Since our repositories commit, we should probably commit here too or rely on the main transaction.
        # Given the repo pattern used (commit in create), let's commit here.
        await self.session.commit()
