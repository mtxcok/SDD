from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import auth, agents, allocations, tasks, misc

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents", tags=["agents"])
app.include_router(allocations.router, prefix=f"{settings.API_V1_STR}/allocations", tags=["allocations"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
app.include_router(misc.router, prefix=f"{settings.API_V1_STR}", tags=["misc"])

@app.get("/")
async def root():
    return {"message": "Welcome to Compute Resource Maintenance System API"}
