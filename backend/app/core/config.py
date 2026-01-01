from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Compute Resource Maintenance System"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "mysql+aiomysql://user:pass@localhost:3306/db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    JWT_SECRET: str = "changethis"  # Should be changed in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # FRP
    FRP_SERVER_ADDR: str = "frps.example.com"
    FRP_SERVER_PORT: int = 7000
    FRP_TOKEN: str = "frp_token"
    
    # Port Pool
    PORT_MIN: int = 50000
    PORT_MAX: int = 60000
    
    # Heartbeat
    HEARTBEAT_TIMEOUT_SEC: int = 90

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
