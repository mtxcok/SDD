@echo off
echo [MOCK] frpc started with args: %*
python "%~dp0mock_frpc.py" %*
