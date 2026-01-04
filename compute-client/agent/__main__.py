from __future__ import annotations

import time
from pathlib import Path

from agent.config import Config
from agent.logger import build_logger
from agent.heartbeat import Heartbeater
from agent.runtime_state import RuntimeState
from agent.api import API
from agent.process import ProcManager, CodeServerManager, FrpcManager
from agent.tasks import TaskRunner

CREDENTIALS_FILE = Path("runtime/credentials.json")

def main():
    # 1) 读配置 & 日志
    cfg = Config.load("work.env")
    log = build_logger("agent", cfg.log_level, cfg.work_dir)

    # 2) 读/写本地凭据
    state = RuntimeState(cfg.work_dir / "credentials.json")

    # 3) 初始化 API 客户端（先带上已有 token）
    api = API(
        base_url=cfg.api_base_url,
        agent_name=cfg.agent_name,
        agent_secret=cfg.agent_secret,
        agent_token=state.agent_token,
    )

    # 4) 若无 token，先注册
    if not state.agent_token:
        log.info("No token found, registering ...")
        reg = api.register()
        state.agent_id = reg.agent_id
        state.agent_token = reg.agent_token
        state.save()
        log.info("Registered ok, got token: %s", reg.agent_token[:6] + "***")
    else:
        log.info("Loaded cached token, id=%s", state.agent_id)

    # managers
    proc_mgr = ProcManager(cfg.work_dir, log)
    code_mgr = CodeServerManager(cfg, proc_mgr, log)
    frp_mgr = FrpcManager(cfg, proc_mgr, log)
    runner = TaskRunner(cfg, api, proc_mgr, code_mgr, frp_mgr)

    # 5) 启动心跳器，on_beat 回调上报
    hb = Heartbeater(
        cfg.heartbeat_interval_sec,
        log,
        on_beat=lambda cpu, mem: _safe_heartbeat(
            api, log, cpu, mem, code_mgr
        ),
    )
    hb.start_background()

    log.info("Agent booting... name=%s work_dir=%s", cfg.agent_name, cfg.work_dir)

    try:
        while True:
            try:
                tasks = api.poll_tasks()
                for t in tasks:
                    runner.handle(t)
            except Exception as e:
                log.warning("poll tasks failed: %s", e)
            time.sleep(cfg.poll_interval_sec)
    except KeyboardInterrupt:
        log.info("Shutting  down...")
        hb.stop()


def _safe_heartbeat(api: API, log, cpu: float, mem: float, code_mgr=None):
    # 1) 正常上报
    try:
        api.heartbeat(cpu=cpu, mem=mem)
    except Exception as e:
        log.warning("heartbeat send failed: %s", e)

    # 2) 额外健康检查：code-server
    # 只有当 code-server 处于“应该运行”的状态（即 handle 不为空）时，才进行健康检查
    # 避免 Agent 刚启动（或被显式停止后）就自动重启它
    if code_mgr and code_mgr.handle and not code_mgr.healthy():
        log.warning("code-server unhealthy (crashed?), restarting...")
        try:
            code_mgr.stop()
            code_mgr.start(password="auto")
            log.info("code-server restarted ok")
        except Exception as e:
            log.error("failed to restart code-server: %s", e)


if __name__ == "__main__":
    main()
