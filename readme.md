# Flask Anthropic 代理

本项目是一个 Flask 应用程序，用于使用 Google Cloud 服务账号凭据与 Anthropic API 交互。它包括生成和验证 API 密钥的功能，确保安全访问。

## 功能

- 生成和验证 API 密钥以确保安全访问。
- 自动刷新 Google Cloud 服务账号凭据。
- 代理请求到 Anthropic API。

## 前提条件

- Python 3.7+
- Google Cloud SDK
- 具有必要权限的服务账号

## 设置步骤

### 第一步：克隆仓库

```bash
git clone https://github.com/syuchua/gcp_claude_transfer.git
cd gcp_claude_transfer
```

### 第二步：安装依赖
建议使用虚拟环境：
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 第三步：安装和配置 Google Cloud SDK
  #### 在 Windows 上
  下载 [Cloud SDK 安装程序](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe?hl=zh-cn)。
  运行安装程序并按照提示完成安装。
  打开命令提示符并初始化 SDK：
  ```
  bash
  gcloud init
  ```
  #### 在 macOS 上
  打开终端。
  使用 Homebrew 安装 Google Cloud SDK：
  ```
  bash
  brew install --cask google-cloud-sdk
  ```
  初始化 SDK:
  ```
  bash
  gcloud init
  ```
  #### 在 Linux 上
  打开终端。
  下载最新版本的 SDK：
  ```
  bash
  curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
  ```
  解压文件并运行安装脚本：
  ```
  bash
  tar -xf google-cloud-cli-linux-x86_64.tar.gz
  ./google-cloud-sdk/install.sh
  ```
  初始化 SDK：
  ```
  bash
  gcloud init
  ```
### 第四步：设置 Google Cloud 服务账号
  访问 Google Cloud Console。

  创建一个新项目或选择一个现有项目。

  启用必要的 API（例如，Anthropic API、Cloud Resource Manager API）。

  创建服务账号：

  进入 IAM & Admin > Service Accounts。
  点击“创建服务账号”。
  输入名称并点击“创建”。
  分配必要的角色（例如，项目编辑者，Anthropic API 用户）。
  点击“完成”。
  创建并下载服务账号的密钥：

  点击你创建的服务账号。
  进入“密钥”标签。
  点击“添加密钥” > “创建新密钥”。
  选择“JSON”并点击“创建”。
  下载 JSON 文件并妥善保存。

### 第四步：配置应用程序
  将下载的服务账号 JSON 文件放在项目目录中。
  设置环境变量以指向服务账号文件：
  ```
  export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service_account.json"
  ```
  或者在脚本中直接设置（如果在 Windows 上运行）：
  ```
  SERVICE_ACCOUNT_FILE = 'C:\\path\\to\\your\\service_account.json'
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE
  ```

### 第五步 运行程序

```
python gcp.py
```

### 第六步，配置nginx(可选)
这是一个简单的模板
```
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## API 端点
生成 API 密钥
URL: /generate_api_key
方法: POST
响应: 返回生成的 API 密钥的 JSON。
```
curl -X POST http://your_domain_or_ip/generate_api_key
```

## 代理请求
URL: /v1/messages
方法: POST
Headers: API-Key（或 Authorization: Bearer <API_KEY>）
Body: 包含消息数据的 JSON。

示例请求：
```
 curl -X POST http://localhost:5000/v1/messages \                                                                   ─╯
-H "API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
  "messages": [
    {
      "role": "user",
      "content": "hello!"
    }
  ],
  "max_tokens": 150
}'
```

## 故障排除
  确保 Google Cloud SDK 已正确安装并配置。
  检查服务账号 JSON 文件的路径是否正确。
  确保在生成 API 密钥后，将其保存并使用于请求中。
