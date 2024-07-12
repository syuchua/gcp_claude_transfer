import os
import json
import threading
from anthropic import AnthropicVertex
from google.oauth2 import service_account
import requests
from flask import Flask, request, redirect, session, url_for, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import secrets
import uuid
from loguru import logger
from google.auth import default

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 生成一个安全的随机密钥

# 设置环境变量以允许不安全的传输
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
SERVICE_ACCOUNT_FILE = 'C:\\path\\to\\your\\service_account.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE

API_KEYS_FILE = './api_keys.json'

# 持久化 API 密钥
def save_api_keys():
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(api_keys, f)

# 加载 API 密钥
def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}


# 生成API密钥
@app.route('/generate_api_key', methods=['POST'])
def generate_key():
    new_key = str(uuid.uuid4())
    api_keys[new_key] = True
    save_api_keys()
    return jsonify({"api_key": new_key})

# 验证 API 密钥
def validate_api_key(key):
    return key in api_keys

# 初始化 API 密钥
api_keys = load_api_keys()

# 获取服务账号凭据
def get_service_account_credentials():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    if credentials.expired:
        credentials.refresh(Request())
    return credentials

def refresh_credentials_periodically():
    try:
        credentials = get_service_account_credentials()
        if credentials.expired:
            credentials.refresh(Request())
            logger.info("Credentials refreshed successfully.")
        threading.Timer(3600, refresh_credentials_periodically).start()  # 每小时刷新一次
    except Exception as e:
        logger.error(f"Error refreshing credentials: {e}")

# 启动定期刷新线程
refresh_credentials_periodically()

# 中转API
@app.route('/v1/messages', methods=['POST'])
def proxy():
    api_key = request.headers.get('API-Key') or request.headers.get('Authorization')
    if api_key and api_key.startswith('Bearer '):
        api_key = api_key.split(' ')[1]  # 提取真正的密钥
    logger.info("Received API key: %s", api_key)
    if not validate_api_key(api_key):
        logger.error("Invalid API key received: %s", api_key)
        return jsonify({"error": "Invalid API key"}), 403

    credentials = get_service_account_credentials()

    data = request.json
    if 'messages' not in data:
        return jsonify({"error": "Field 'messages' is required"}), 400

    try:
        logger.info("Received request data: %s", data)
        # 使用AnthropicVertex类进行调用
        LOCATION = "europe-west1"  # 或 "us-east5"
        client = AnthropicVertex(region=LOCATION, project_id=credentials.project_id)

        logger.info("Created AnthropicVertex client successfully.")
        logger.info("Calling client.messages.create with messages: %s", data['messages'])
        response = client.messages.create(
            system="You are a helpful assistant.",
            max_tokens=data.get('max_tokens', 2048),
            messages=data['messages'],
            model="claude-3-5-sonnet@20240620"
        )

        logger.info("Received response from AnthropicVertex: %s", response)

        return jsonify(response.model_dump())
    except Exception as e:
        logger.error("Error during API request: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=None)
