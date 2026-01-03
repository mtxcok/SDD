from __future__ import annotations

import httpx
from pydantic import BaseModel
from pathlib import Path


class RegisterResp(BaseModel):
    agent_id: str
    agent_token: str


class API:
    """
    超迷你电话机：
      – register()  -> POST /agents/register
      – heartbeat() -> POST /agents/heartbeat
      – poll_tasks() -> GET /agents/tasks
    """

    def __init__(self, base_url: str, agent_name: str, agent_secret: str, agent_token: str | None = None):
        self.base = base_url.rstrip("/")
        self.agent_name = agent_name
        self.agent_secret = agent_secret
        self.agent_token = agent_token
        # 用同一个 httpx.Client 复用连接池
        self.client = httpx.Client(timeout=5)

    # ---------- 辅助 ----------
    def _headers(self):
        """如果已有 token 就带上"""
        hdr = {"Content-Type": "application/json"}
        if self.agent_token:
            hdr["Authorization"] = f"Bearer {self.agent_token}"
        return hdr
    
    class AuthError(Exception):
        pass

    # ------------------------ internal helper ------------------------
    def _request(self, method: str, path: str, **kw):
        """统一发送请求；捕获 401 并自动重新注册、重试一次"""
        url = f"{self.base}{path}"
        kw.setdefault("headers", self._headers())
        resp = self.client.request(method, url, **kw)

        if resp.status_code == 401:
            print("Token expired or invalid, re-registering...")
            self.agent_token = None
            try:
                # 调用原始 register 拿到新 token
                reg = self.register()
                # 把新 token 写回本地
                from agent.runtime_state import RuntimeState
                from pathlib import Path
                state = RuntimeState(Path("runtime/credentials.json"))
                state.agent_id = reg.agent_id
                state.agent_token = reg.agent_token
                state.save()
                # 用新 token 重试一次
                kw["headers"] = self._headers()
                resp = self.client.request(method, url, **kw)
            except Exception as e:
                raise Exception("re-register failed") from e

        resp.raise_for_status()
        return resp

    # ---------- API 调用 ----------
    def register(self) -> RegisterResp:
        resp = self.client.post(
            f"{self.base}/agents/register",
            json={"name": self.agent_name, "secret": self.agent_secret},
            headers=self._headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        reg = RegisterResp.model_validate(data)
        self.agent_token = reg.agent_token  # 缓存下来，后面请求带上
        return reg

    def heartbeat(self, cpu: float, mem: float):
        payload = {"cpu": cpu, "mem": mem}
        resp = self._request("POST", "/agents/heartbeat", json=payload)
        return resp.json()

    def poll_tasks(self) -> list[dict]:
        resp = self._request("GET", "/agents/tasks")
        return resp.json() # 期待是 list

    # ------------------------ new: report ------------------------
    def report_task(self, task_id: str, status: str, message: str | None = None):
        payload = {"status": status, "message": message}
        resp = self._request("POST", f"/agents/tasks/{task_id}/report", json=payload)
        return resp.json()