import requests
import json
import sys
import os

# 配置
BASE_URL = "http://localhost:8000/api/v1"
CREDENTIALS_PATH = r"..\compute-client\runtime\credentials.json"

def run():
    print("-" * 50)
    print("触发 Agent 任务脚本")
    print("-" * 50)

    # 1. 读取 Agent 凭据
    try:
        with open(CREDENTIALS_PATH, "r") as f:
            creds = json.load(f)
            agent_id = creds.get("agent_id")
            agent_token = creds.get("agent_token")
            if not agent_id:
                print("❌ 未在 credentials.json 中找到 agent_id")
                return
            print(f"✅ 读取到 Agent ID: {agent_id}")
    except FileNotFoundError:
        print(f"❌ 找不到凭据文件: {CREDENTIALS_PATH}")
        return

    # 2. 登录管理员 (为了调用 allocation 接口)
    # 这里简化处理，直接注册一个临时管理员，或者使用已知的管理员
    # 假设我们注册一个新的临时管理员来操作
    admin_name = "admin_trigger"
    admin_pass = "password123"
    
    # 尝试登录，如果失败则注册
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": admin_name, "password": admin_pass})
    if resp.status_code != 200:
        print("   -> 管理员未注册，正在注册...")
        requests.post(f"{BASE_URL}/auth/register", json={"username": admin_name, "password": admin_pass})
        resp = requests.post(f"{BASE_URL}/auth/login", data={"username": admin_name, "password": admin_pass})
    
    if resp.status_code != 200:
        print(f"❌ 管理员登录失败: {resp.text}")
        return
    
    admin_token = resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ 管理员登录成功")

    # 3. 申请分配 (这将触发 start_code_server 任务)
    print(f"3. 为 Agent {agent_id} 申请 Code Server...")
    resp = requests.post(f"{BASE_URL}/allocations/create", json={
        "agent_id": agent_id,
        "service": "code_server"
    }, headers=admin_headers)
    
    if resp.status_code != 200:
        print(f"❌ 申请失败: {resp.text}")
        return
    
    alloc = resp.json()
    print(f"✅ 申请成功! Allocation ID: {alloc['id']}")
    print(f"   -> 请观察 Agent 终端，应该会收到 'start_code_server' 任务")

if __name__ == "__main__":
    run()
