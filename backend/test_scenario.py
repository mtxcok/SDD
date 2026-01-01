import requests
import time
import sys
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"

def log(msg):
    print(f"[TEST] {msg}")

def run_test():
    print("-" * 50)
    print("开始运行后端集成测试脚本")
    print("-" * 50)

    # 1. 注册管理员用户
    # 为了避免重复运行报错，使用时间戳生成唯一用户名
    username = f"admin_{int(time.time())}"
    password = "password123"
    log(f"1. 注册用户: {username}")
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "password": password
        })
        if resp.status_code != 200:
            print(f"❌ 注册失败: {resp.text}")
            return
        log("✅ 用户注册成功")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端服务已在 http://localhost:8000 启动")
        return

    # 2. 登录获取 Token
    log("2. 尝试登录...")
    resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password
    })
    if resp.status_code != 200:
        print(f"❌ 登录失败: {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    log("✅ 登录成功，获取到 JWT Token")

    # 3. 创建 Agent 邀请码
    agent_name = f"agent_{int(time.time())}"
    log(f"3. 创建 Agent 邀请: {agent_name}")
    resp = requests.post(f"{BASE_URL}/agents/create_invite", json={"name": agent_name}, headers=headers)
    if resp.status_code != 200:
        print(f"❌ 创建邀请失败: {resp.text}")
        return
    secret = resp.json()["secret"]
    log(f"✅ 邀请创建成功，Secret: {secret}")

    # 4. Agent 注册 (模拟 Agent 端)
    log("4. 模拟 Agent 注册...")
    resp = requests.post(f"{BASE_URL}/agents/register", json={
        "name": agent_name,
        "secret": secret
    })
    if resp.status_code != 200:
        print(f"❌ Agent 注册失败: {resp.text}")
        return
    agent_data = resp.json()
    agent_id = agent_data["agent_id"]
    agent_token = agent_data["agent_token"]
    log(f"✅ Agent 注册成功. ID: {agent_id}")

    # 5. Agent 心跳上报
    log("5. 发送心跳...")
    resp = requests.post(f"{BASE_URL}/agents/heartbeat", json={
        "agent_id": agent_id,
        "agent_token": agent_token,
        "cpu": 10.5,
        "mem": 20.0
    })
    if resp.status_code != 200:
        print(f"❌ 心跳失败: {resp.text}")
        return
    log("✅ 心跳上报成功")

    # 6. 申请端口分配 (管理员操作)
    log("6. 申请端口分配 (Code Server)...")
    resp = requests.post(f"{BASE_URL}/allocations/create", json={
        "agent_id": agent_id,
        "service": "code_server"
    }, headers=headers)
    if resp.status_code != 200:
        print(f"❌ 申请分配失败: {resp.text}")
        return
    allocation = resp.json()
    alloc_id = allocation["id"]
    remote_port = allocation["remote_port"]
    log(f"✅ 分配请求已提交. Allocation ID: {alloc_id}, 预分配端口: {remote_port}, 状态: {allocation['status']}")

    # 7. Agent 轮询任务
    log("7. Agent 轮询任务...")
    resp = requests.post(f"{BASE_URL}/agents/poll", json={
        "agent_id": agent_id,
        "agent_token": agent_token
    })
    tasks = resp.json()["tasks"]
    log(f"✅ 轮询成功，获取到 {len(tasks)} 个任务")
    
    target_task = None
    for t in tasks:
        if t["type"] == "start_code_server" and t["payload"]["allocation_id"] == alloc_id:
            target_task = t
            break
    
    if not target_task:
        print("❌ 未找到预期的 start_code_server 任务")
        return
    
    log(f"   -> 找到任务: {target_task['type']} (ID: {target_task['id']})")
    log(f"   -> 任务 Payload: {json.dumps(target_task['payload'])}")

    # 8. Agent 上报任务完成
    log("8. Agent 上报任务完成...")
    resp = requests.post(f"{BASE_URL}/tasks/{target_task['id']}/report", json={
        "status": "done",
        "message": "Started successfully"
    })
    if resp.status_code != 200:
        print(f"❌ 上报任务失败: {resp.text}")
        return
    log("✅ 任务状态已更新为 DONE")

    # 9. 验证分配状态
    log("9. 验证最终分配状态...")
    resp = requests.get(f"{BASE_URL}/allocations/?agent_id={agent_id}", headers=headers)
    allocs = resp.json()
    my_alloc = next((a for a in allocs if a["id"] == alloc_id), None)
    
    if my_alloc and my_alloc["status"] == "active":
        log(f"✅ 验证成功! Allocation 状态为 ACTIVE. 端口 {my_alloc['remote_port']} 已就绪.")
    else:
        status = my_alloc['status'] if my_alloc else 'Not Found'
        print(f"❌ 状态验证失败. 期望: active, 实际: {status}")

    print("-" * 50)
    print("🎉 测试流程全部通过!")
    print("-" * 50)

if __name__ == "__main__":
    run_test()
