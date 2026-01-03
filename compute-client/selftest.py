from __future__ import annotations

import os, sys, time, signal, subprocess, textwrap, pathlib, shutil

BASE = pathlib.Path(__file__).parent.resolve()
PY = str(BASE / ".venv" / "bin" / "python")            # 当前解释器；确保已激活 .venv

# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def run(cmd, **kw):
    print("$", " ".join(cmd))
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **kw,
    )

def write_mock_server():
    code = textwrap.dedent(
        """
        from fastapi import FastAPI, HTTPException, Request
        import uvicorn

        app = FastAPI()
        agents = {}

        @app.post("/agents/register")
        async def register(data: dict):
            if data.get("secret") != "topsecret":
                raise HTTPException(status_code=401, detail="bad secret")
            agents[data["name"]] = "tok_" + data["name"]
            return {"agent_id": data["name"], "agent_token": agents[data["name"]]}

        @app.post("/agents/heartbeat")
        async def heartbeat(req: Request, data: dict):
            tok = req.headers.get("authorization", "")[7:]
            if tok not in agents.values():
                raise HTTPException(status_code=401)
            return {"ok": True}

        @app.get("/agents/tasks")
        async def tasks(req: Request):
            tok = req.headers.get("authorization", "")[7:]
            if tok not in agents.values():
                raise HTTPException(status_code=401)
            if not getattr(app.state, "sent_once", False):
                app.state.sent_once = True
                return [{
                    "id": "t1",
                    "type": "start_code_server",
                    "payload": {"password": "hello123"}
                }]
            return []

        @app.post("/agents/tasks/{task_id}/report")
        async def report(task_id: str, req: Request, data: dict):
            tok = req.headers.get("authorization", "")[7:]
            if tok not in agents.values():
                raise HTTPException(status_code=401)
            print(f"[REPORT] {task_id} {data}")
            return {"ok": True}

        if __name__ == "__main__":
            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
        """
    )
    (BASE / "mock_server.py").write_text(code)

# ----------------------------------------------------------------------
def main() -> None:
    # 0) 环境检查
    cred = BASE / "runtime/credentials.json"
    if cred.exists():
        cred.unlink()  # 保证每次重新注册

    # 1) 写/更新 mock_server.py
    write_mock_server()

    # 2) 启动 mock_server
    mock = run([PY, "mock_server.py"], cwd=BASE)

    # 3) 启动 Agent （API_BASE_URL 指向 mock）
    env = os.environ.copy()
    env["API_BASE_URL"] = "http://127.0.0.1:8000"
    agent = run([PY, "-m", "agent"], cwd=BASE, env=env)

    # 4) 监听输出，等待报告
    ok = False
    t0 = time.time()
    try:
        while time.time() - t0 < 60:
            line = agent.stdout.readline()
            if line:
                print("AG:", line.rstrip())
                if "[REPORT] t1" in line:
                    ok = True
                    break
            if agent.poll() is not None:  # agent 进程退出
                break
    finally:
        # 5) 收尾：终止进程
        for p in (agent, mock):
            if p.poll() is None:
                p.send_signal(signal.SIGINT)
                try:
                    p.wait(3)
                except subprocess.TimeoutExpired:
                    p.kill()

    print("\n=== RESULT ===")
    print("PASS" if ok else "FAIL")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()