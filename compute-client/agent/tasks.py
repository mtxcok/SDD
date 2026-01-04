from __future__ import annotations

from agent.process import CodeServerManager, ProcManager, FrpcManager
from agent.logger import build_logger


class TaskRunner:
    """
    把后端下发的任务 dict -> 调用对应的 Manager。
    目前支持:
      - start_code_server  payload = {password, remote_port}
      - stop_code_server   payload = {}
    """

    def __init__(
        self,
        cfg,
        api,
        proc_mgr: ProcManager,
        code_mgr: CodeServerManager,
        frp_mgr: FrpcManager,
    ):
        self.cfg = cfg
        self.api = api
        self.pm = proc_mgr
        self.code_mgr = code_mgr
        self.frp_mgr = frp_mgr
        self.log = build_logger("TaskRunner", cfg.log_level, cfg.work_dir)

    # ----------------------------- public -----------------------------
    def handle(self, task: dict):
        tid = task.get("id", "<no-id>")
        ttype = task.get("type")
        payload = task.get("payload", {})

        if ttype == "start_code_server":
            self._handle_start(tid, payload)
        elif ttype == "stop_code_server":
            self._handle_stop(tid)
        else:
            self.log.warning("Unknown task type %s", ttype)

    # ----------------------------- internal ---------------------------
    def _handle_start(self, tid: str, payload: dict):
        pw = payload.get("password", "123456")
        remote_port = int(payload.get("remote_port", 32001))

        # start code-server
        cs_handle = self.code_mgr.start(password=pw)
        local_port = self.code_mgr.port

        # start frpc
        self.frp_mgr.start(remote_port=remote_port, local_port=local_port)
        self.log.info("Task %s done: code-server(pid=%s) -> remote %s", tid, cs_handle.popen.pid, remote_port)
        self.api.report_task(tid, "done", f"remote_port={remote_port}")

    def _handle_stop(self, tid: str):
        self.frp_mgr.stop()
        self.code_mgr.stop()
        self.log.info("Task %s done: stopped code-server + frpc", tid)
        self.api.report_task(tid, "done", "stopped")