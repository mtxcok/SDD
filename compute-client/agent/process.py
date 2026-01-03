from __future__ import annotations

import os
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence


@dataclass
class ProcHandle:
    name: str
    popen: subprocess.Popen
    start_time: float
    stdout_path: Optional[Path] = None
    stderr_path: Optional[Path] = None


class ProcManager:
    """一个很听话的“开关机按钮”。

    - start(): 以你给的命令启动进程，stdout/stderr 重定向到文件。
    - is_running(): 看进程还在不在。
    - stop(): 温柔终止，超时就强制结束。
    """

    def __init__(self, work_dir: Path, logger):
        self.work_dir = work_dir
        self.log = logger
        (self.work_dir / "logs").mkdir(parents=True, exist_ok=True)

    def start(
        self,
        cmd: Sequence[str],
        *,
        name: str,
        env: Optional[dict] = None,
        cwd: Optional[Path] = None,
        stdout_file: Optional[Path] = None,
        stderr_file: Optional[Path] = None,
        creationflags: int = 0,
    ) -> ProcHandle:
        stdout_path = stdout_file or (self.work_dir / "logs" / f"{name}.out.log")
        stderr_path = stderr_file or (self.work_dir / "logs" / f"{name}.err.log")
        stdout_f = open(stdout_path, "a", encoding="utf-8")
        stderr_f = open(stderr_path, "a", encoding="utf-8")
        env_final = os.environ.copy()
        if env:
            env_final.update(env)
        pop = subprocess.Popen(
            list(cmd),
            stdout=stdout_f,
            stderr=stderr_f,
            cwd=str(cwd) if cwd else None,
            env=env_final,
            creationflags=creationflags,
        )
        self.log.info("proc '%s' started (pid=%s)", name, pop.pid)
        return ProcHandle(name=name, popen=pop, start_time=time.time(), stdout_path=stdout_path, stderr_path=stderr_path)

    @staticmethod
    def is_running(ph: ProcHandle) -> bool:
        return ph.popen.poll() is None

    def stop(self, ph: ProcHandle, timeout: float = 5.0):
        if ph.popen.poll() is None:
            self.log.info("stopping '%s' (pid=%s)", ph.name, ph.popen.pid)
            try:
                ph.popen.terminate()
            except Exception:
                pass
            t0 = time.time()
            while time.time() - t0 < timeout:
                if ph.popen.poll() is not None:
                    break
                time.sleep(0.1)
            if ph.popen.poll() is None:
                self.log.warning("force killing '%s' (pid=%s)", ph.name, ph.popen.pid)
                try:
                    ph.popen.kill()
                except Exception:
                    pass
        else:
            self.log.info("'%s' already stopped (code=%s)", ph.name, ph.popen.returncode)


def parse_bind(bind: str) -> tuple[str, int]:
    """把 "127.0.0.1:8080" 拆成 (host, port)。"""
    if ":" not in bind:
        raise ValueError(f"invalid bind: {bind}")
    host, port_s = bind.rsplit(":", 1)
    return host, int(port_s)


def port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


class CodeServerManager:
    """
    负责：
    - 启动 code-server（需要系统已安装 `code-server` 并在 PATH 中）
    - 健康检查（端口是否在监听）
    - 停止进程
    """

    def __init__(self, cs_bind: str, proc_mgr: ProcManager, logger):
        self.host, self.port = parse_bind(cs_bind)
        self.pm = proc_mgr
        self.log = logger
        self.handle: Optional[ProcHandle] = None

    def start(self, password: str) -> ProcHandle:
        if self.handle and self.pm.is_running(self.handle):
            self.log.info("code-server already running (pid=%s)", self.handle.popen.pid)
            return self.handle
        env = {"PASSWORD": password}
        cmd = [
            "code-server",
            "--bind-addr",
            f"{self.host}:{self.port}",
            "--auth",
            "password",
            "--disable-telemetry",
        ]
        self.handle = self.pm.start(cmd, name="code-server", env=env)
        return self.handle

    def stop(self):
        if self.handle:
            self.pm.stop(self.handle)
            self.handle = None
    
    def healthy(self) -> bool:
        """进程存在且端口可联通"""
        return (
            self.handle and
            self.pm.is_running(self.handle) and
            port_open(self.host, self.port)
        )

# --------------------------- FRPC MANAGER ---------------------------
class FrpcManager:
    """启动 / 停止 frpc，并动态写 frpc.ini"""
    def __init__(self, cfg, proc_mgr: ProcManager, logger):
        self.cfg = cfg
        self.pm = proc_mgr
        self.log = logger
        self.handle = None

    def _write_ini(self, remote_port: int, local_port: int):
        ini_path = self.pm.work_dir / "frpc.ini"
        ini_path.write_text(
            f"[common]\\n"
            f"server_addr = {self.cfg.frp_server_addr}\\n"
            f"server_port = {self.cfg.frp_server_port}\\n"
            f"token = {self.cfg.frp_token}\\n\\n"
            f"[code_server_{remote_port}]\\n"
            f"type = tcp\\n"
            f"local_ip = 127.0.0.1\\n"
            f"local_port = {local_port}\\n"
            f"remote_port = {remote_port}\\n"
        )
        return ini_path

    def start(self, *, remote_port: int, local_port: int):
        if self.handle and self.pm.is_running(self.handle):
            self.log.info("frpc already running")
            return
        ini = self._write_ini(remote_port, local_port)
        self.handle = self.pm.start(["frpc", "-c", str(ini)], name="frpc")

    def stop(self):
        if self.handle:
            self.pm.stop(self.handle)
            self.handle = None