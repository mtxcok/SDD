# Distributed Cloud Development Platform (SDD)

## 📖 项目简介

这是一个**分布式云开发环境管理平台**。它的核心功能是让用户能够通过一个统一的 Web 界面，管理分布在不同机器上的计算节点（Agent），并按需在这些节点上动态创建、访问和销毁远程开发环境（VS Code / code-server）。

简单来说，它就像是一个**私有版的 GitHub Codespaces** 或 **Coder**。

### 核心价值
1.  **统一管理**：在一个面板上监控所有计算节点的状态（CPU、内存、在线状态）。
2.  **按需分配**：用户点击“Start Session”，系统自动在远程机器上启动 VS Code 环境。
3.  **内网穿透**：集成了 FRP (Fast Reverse Proxy)，即使计算节点在内网（如家庭 PC、公司内网服务器），用户也能通过公网链接直接访问开发环境。

---

## 🏗️ 系统架构

系统由三个主要部分组成：

1.  **Backend (控制面)**
    *   **技术栈**: Python FastAPI, SQLAlchemy, Redis (可选)
    *   **职责**: 负责用户认证、Agent 管理、任务分发、端口分配以及状态维护。它是整个系统的大脑。

2.  **Frontend (用户面)**
    *   **技术栈**: Vue 3, TypeScript, Ant Design Vue, Pinia
    *   **职责**: 提供可视化的管理界面。用户在这里查看 Agent 列表，点击按钮启动环境，并获取访问链接。

3.  **Compute Client / Agent (数据面)**
    *   **技术栈**: Python
    *   **职责**: 运行在实际的计算节点上（如你的高性能台式机或云服务器）。
    *   **工作流**:
        1.  启动时向 Backend 注册并保持心跳。
        2.  轮询获取任务（如 `start_code_server`）。
        3.  执行任务：启动 `code-server` 进程，并配置 `frpc` 进行端口映射。
        4.  向 Backend 汇报任务完成，生成访问链接。

---

## 🚀 功能特性

*   **Agent 自动注册与发现**: 只需在目标机器运行 Agent 脚本，即可自动接入平台。
*   **实时资源监控**: 实时查看各节点的 CPU 和内存占用情况。
*   **动态环境配置**: 自动分配端口，自动生成访问密码，无需手动配置。
*   **Mock 模式支持**: 项目包含完整的 Mock 实现（Mock Code Server 和 Mock FRPC），方便在没有真实业务环境的情况下进行全链路开发和测试。

---

## 🛠️ 快速开始 (开发模式)

### 1. 环境准备
*   Python 3.10+
*   Node.js 16+
*   Redis (可选，开发模式下部分功能可跳过)

### 2. 启动后端 (Backend)
```bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 启动服务 (默认端口 8000)
uvicorn app.main:app --reload
```

### 3. 启动前端 (Frontend)
```bash
cd ssd-frontend
# 安装依赖
npm install
# 启动开发服务器 (默认端口 5173)
npm run dev
```

### 4. 启动计算节点 (Agent)
```bash
cd compute-client
# 安装依赖
pip install -r requirements.txt
# 启动 Agent
python -m agent.main
```

---

## 🧪 测试流程 (Mock 模式)

本项目当前配置了 Mock 工具，用于模拟真实的业务负载：

1.  **启动全栈**：分别启动 Backend, Frontend 和 Agent。
2.  **访问前端**：打开浏览器访问 `http://localhost:5173`，登录（默认账号通常在 `backend/app/core/database.py` 或注册新账号）。
3.  **查看 Agent**：在 Agent Management 页面，你应该能看到一个状态为 `ONLINE` 的 Agent。
4.  **创建会话**：点击 **"Start Session"**。
    *   Backend 会生成一个 `start_code_server` 任务。
    *   Agent 收到任务，启动 `mock_service.py` (模拟 VS Code) 和 `mock_frpc.py` (模拟端口转发)。
5.  **访问服务**：等待几秒，界面上的状态变为 `ACTIVE`，点击生成的链接（如 `http://127.0.0.1:54498`）。
6.  **验证**：你应该能看到 "Mock Code Server is running..." 的欢迎页面。

---

## 📂 目录结构

```
d:\SDD
├── backend/            # FastAPI 后端代码
│   ├── app/
│   │   ├── api/        # API 路由
│   │   ├── models/     # 数据库模型
│   │   └── services/   # 业务逻辑
├── ssd-frontend/       # Vue3 前端代码
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   └── stores/     # 状态管理
├── compute-client/     # Agent 客户端代码
│   ├── agent/          # 核心逻辑
│   ├── mock_bin/       # 模拟脚本 (mock_service.py, mock_frpc.py)
│   └── runtime/        # 运行时目录 (日志, 配置文件)
└── README.md           # 项目说明文档
```