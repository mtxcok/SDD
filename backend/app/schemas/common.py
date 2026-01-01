from pydantic import BaseModel

class OkResponse(BaseModel):
    ok: bool = True

class HealthResponse(BaseModel):
    status: str = "ok"

class PortsAvailableResponse(BaseModel):
    min: int
    max: int
    allocated_count: int
