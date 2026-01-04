from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import auth, agents, allocations, tasks, misc

app = FastAPI(title=settings.PROJECT_NAME)

# 配置 CORS
# Ensure CORS is set up for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改为具体的域名列表
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents", tags=["agents"])
app.include_router(allocations.router, prefix=f"{settings.API_V1_STR}/allocations", tags=["allocations"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
app.include_router(misc.router, prefix=f"{settings.API_V1_STR}", tags=["misc"])

@app.get("/")
async def root():
    return {"message": "Welcome to Compute Resource Maintenance System API"}
