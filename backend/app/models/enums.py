import enum

class AgentStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class AllocationStatus(str, enum.Enum):
    REQUESTED = "requested"
    STARTING = "starting"
    ACTIVE = "active"
    RELEASING = "releasing"
    RELEASED = "released"
    FAILED = "failed"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    DONE = "done"
    FAILED = "failed"

class ActorType(str, enum.Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
