from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict

class Config(BaseModel):
  model_config = ConfigDict(populate_by_name=True, extra="ignore")
  agent_name: str = Field(default="agent-01", alias="AGENT_NAME")
  agent_secret: str = Field(default="replace-with-temporary-secret", alias="AGENT_SECRET")
  api_base_url: str = Field(default="http://your-backend-api:8000", alias="API_BASE_URL")
  frp_server_addr: str = Field(default="your.frps.ip.or.domain", alias="FRP_SERVER_ADDR")
  frp_server_port: int = Field(default=7000, alias="FRP_SERVER_PORT")
  frp_token: str = Field(default="replace-with-frp-token", alias="FRP_TOKEN")
  cs_bind: str = Field(default="127.0.0.1:8080", alias="CS_BIND")
  heartbeat_interval_sec: int = Field(default=30, alias="HEARTBEAT_INTERVAL_SEC")
  poll_interval_sec: int = Field(default=5, alias="POLL_INTERVAL_SEC")
  log_level: str = Field(default="INFO", alias="LOG_LEVEL")
  work_dir: Path = Field(default=Path("./runtime"), alias="WORK_DIR")
  @classmethod
  def load(cls, env_file: str = "work.env") -> "Config":
    load_dotenv(env_file, override=False)
    cfg = cls.model_validate(os.environ)
    cfg.work_dir = Path(cfg.work_dir).resolve()
    (cfg.work_dir / "logs").mkdir(parents=True, exist_ok=True)
    return cfg  