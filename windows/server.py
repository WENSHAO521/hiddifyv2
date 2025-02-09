# Hiddify 代码优化 - 性能优化

# 1. 提高代理连接处理速度（异步化）
import asyncio
import aiohttp
from flask import Flask, jsonify, request
import os
from gevent.pywsgi import WSGIServer
import subprocess

app = Flask(__name__)

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

proxy_status = {"running": True, "connected_users": 5, "total_traffic": "1.2GB"}

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify(proxy_status)

@app.route("/set-proxy", methods=["POST"])
def set_proxy():
    data = request.json
    proxy_status["running"] = data.get("running", True)
    return jsonify({"message": "代理状态已更新", "new_status": proxy_status})

@app.route("/traffic", methods=["GET"])
def get_traffic():
    try:
        # 替换 os.popen 使用 subprocess 以提高安全性和兼容性
        sent = subprocess.check_output(["cat", "/sys/class/net/eth0/statistics/tx_bytes"]).decode().strip()
        received = subprocess.check_output(["cat", "/sys/class/net/eth0/statistics/rx_bytes"]).decode().strip()
    except Exception:
        sent, received = "N/A", "N/A"
    return jsonify({"sent": sent, "received": received})

if __name__ == "__main__":
    try:
        http_server = WSGIServer(("0.0.0.0", 5000), app)
        http_server.serve_forever()  # 使用 gevent WSGI 服务器，避免 Flask 运行模式冲突
    except Exception as e:
        print(f"服务器启动失败: {e}")
