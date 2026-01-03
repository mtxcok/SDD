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
