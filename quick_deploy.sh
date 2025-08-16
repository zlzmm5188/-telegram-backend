#!/bin/bash
# Telegram多会话客户端系统 - 快速部署脚本

echo "🚀 Telegram多会话客户端系统 - 快速部署"
echo "=========================================="

# 获取服务器IP
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
fi

echo "📍 服务器IP: $SERVER_IP"
echo ""

# 1. 更新系统并安装基础依赖
echo "📦 安装系统依赖..."
if command -v apt &> /dev/null; then
    sudo apt update -y
    sudo apt install -y python3 python3-pip nodejs npm nginx git curl wget
elif command -v yum &> /dev/null; then
    sudo yum update -y
    sudo yum install -y python3 python3-pip nodejs npm nginx git curl wget
fi

# 2. 安装Python依赖
echo "🐍 安装Python依赖..."
pip3 install --break-system-packages fastapi uvicorn telethon requests

# 3. 创建工作目录
echo "📁 创建工作目录..."
mkdir -p ~/telegram-client
cd ~/telegram-client

# 4. 下载必要文件（如果不存在）
echo "📥 准备项目文件..."

# 创建FastAPI后端
cat > main.py << 'EOF'
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from telethon import TelegramClient
import hashlib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_ID = 27941788
API_HASH = '0cd0979dc85b2433a7648342e7fce258'

def get_session_file(request: Request, phone: str = None):
    host = request.headers.get("host", "localhost")
    print(f"收到请求，Host: {host}")
    
    if '.' in host:
        subdomain = host.split('.')[0]
    else:
        subdomain = 'default'
    
    if phone:
        session_id = hashlib.md5(f"{subdomain}_{phone}".encode()).hexdigest()[:8]
    else:
        session_id = hashlib.md5(subdomain.encode()).hexdigest()[:8]
    
    session_file = f"session_{session_id}.session"
    print(f"使用session文件: {session_file}")
    return session_file

class PhoneModel(BaseModel):
    phone: str

class VerifyModel(BaseModel):
    phone: str
    code: str

class SendModel(BaseModel):
    username: str
    message: str

@app.post("/send_code")
async def send_code(data: PhoneModel, request: Request):
    try:
        session_file = get_session_file(request, data.phone)
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(data.phone)
        await client.disconnect()
        return {"success": True, "msg": "Code sent", "session_file": session_file}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/verify")
async def verify(data: VerifyModel, request: Request):
    try:
        session_file = get_session_file(request, data.phone)
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.connect()
        await client.sign_in(data.phone, data.code)
        await client.disconnect()
        return {"success": True, "session_file": session_file}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/me")
async def me(request: Request):
    try:
        session_file = get_session_file(request)
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.start()
        me = await client.get_me()
        await client.disconnect()
        return {
            "id": me.id,
            "first_name": me.first_name,
            "username": me.username,
            "phone": me.phone,
            "session_file": session_file
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/send")
async def send(data: SendModel, request: Request):
    try:
        session_file = get_session_file(request)
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.start()
        await client.send_message(data.username, data.message)
        await client.disconnect()
        return {"success": True, "session_file": session_file}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/session/status")
async def get_session_status(request: Request):
    try:
        session_file = get_session_file(request)
        import os
        if not os.path.exists(session_file):
            return {"authorized": False, "reason": "Session file not found"}
        
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.connect()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            await client.disconnect()
            return {
                "authorized": True,
                "user": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "username": me.username,
                    "phone": me.phone
                },
                "session_file": session_file
            }
        else:
            await client.disconnect()
            return {"authorized": False, "reason": "Session not authorized"}
            
    except Exception as e:
        return {"authorized": False, "reason": str(e)}

@app.get("/debug/session")
async def debug_session(request: Request):
    import os
    host = request.headers.get("host", "localhost")
    session_file = get_session_file(request)
    return {
        "host": host,
        "subdomain": host.split('.')[0] if '.' in host else 'default',
        "session_file": session_file,
        "file_exists": os.path.exists(session_file)
    }
EOF

# 5. 创建Web客户端
cat > telegram_web_client.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Web客户端</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: #2196F3;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .main-content { display: flex; height: 600px; }
        .sidebar {
            width: 300px;
            background: #f5f5f5;
            border-right: 1px solid #ddd;
            padding: 20px;
            overflow-y: auto;
        }
        .chat-area { flex: 1; display: flex; flex-direction: column; }
        .form-group { margin-bottom: 15px; }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #333;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
            margin: 5px;
        }
        .btn-primary { background: #2196F3; color: white; }
        .btn-success { background: #4CAF50; color: white; }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .send-panel {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
        }
        .send-form { display: flex; gap: 10px; margin-bottom: 10px; }
        .send-form input { flex: 1; padding: 12px; }
        @media (max-width: 768px) {
            .main-content { flex-direction: column; height: auto; }
            .sidebar { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔵 Telegram Web客户端</h1>
            <p>支持多子域名会话管理</p>
        </div>
        
        <div class="main-content">
            <div class="sidebar">
                <h3>连接设置</h3>
                <div class="form-group">
                    <label for="subdomain">子域名:</label>
                    <input type="text" id="subdomain" value="user1" placeholder="例如: user1">
                </div>
                <button class="btn btn-primary" id="checkStatusBtn">检查状态</button>
                
                <h3 style="margin-top: 20px;">快速登录</h3>
                <div class="form-group">
                    <label for="phone">手机号:</label>
                    <input type="text" id="phone" placeholder="+8613800138000">
                </div>
                <button class="btn btn-primary" id="sendCodeBtn">发送验证码</button>
                
                <div class="form-group">
                    <label for="code">验证码:</label>
                    <input type="text" id="code" placeholder="12345">
                </div>
                <button class="btn btn-success" id="verifyBtn">验证登录</button>
                
                <div id="status" style="margin-top: 20px; padding: 10px; border-radius: 6px; background: #f8d7da; color: #721c24;">
                    状态: 未连接
                </div>
            </div>
            
            <div class="chat-area">
                <div class="messages" id="messages">
                    <div class="message">
                        <strong>欢迎使用Telegram Web客户端！</strong><br>
                        1. 输入子域名 (例如: user1)<br>
                        2. 完成快速登录<br>
                        3. 开始发送和接收消息
                    </div>
                </div>
                
                <div class="send-panel">
                    <div class="send-form">
                        <input type="text" id="recipient" placeholder="收件人用户名" disabled>
                        <input type="text" id="messageText" placeholder="输入消息内容..." disabled>
                        <button class="btn btn-primary" id="sendBtn" disabled>发送</button>
                    </div>
                    <button class="btn btn-primary" id="getUserInfoBtn" disabled>获取用户信息</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const baseUrl = window.location.origin;
        
        function addMessage(content, type = 'system') {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            messageDiv.innerHTML = `<div>${new Date().toLocaleTimeString()}</div><div>${content}</div>`;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function makeRequest(endpoint, method = 'GET', data = null) {
            const subdomain = document.getElementById('subdomain').value.trim() || 'default';
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Host': `${subdomain}.example.com`
                }
            };
            if (data) options.body = JSON.stringify(data);
            
            const response = await fetch(`${baseUrl}${endpoint}`, options);
            return await response.json();
        }
        
        document.getElementById('checkStatusBtn').addEventListener('click', async () => {
            try {
                const result = await makeRequest('/session/status');
                if (result.authorized) {
                    document.getElementById('status').innerHTML = `状态: 已连接 - ${result.user.first_name}`;
                    document.getElementById('status').style.background = '#d4edda';
                    document.getElementById('status').style.color = '#155724';
                    ['recipient', 'messageText', 'sendBtn', 'getUserInfoBtn'].forEach(id => 
                        document.getElementById(id).disabled = false
                    );
                } else {
                    document.getElementById('status').innerHTML = `状态: 未授权 - ${result.reason}`;
                }
            } catch (error) {
                addMessage(`检查状态失败: ${error.message}`);
            }
        });
        
        document.getElementById('sendCodeBtn').addEventListener('click', async () => {
            const phone = document.getElementById('phone').value.trim();
            if (!phone) return alert('请输入手机号');
            
            try {
                const result = await makeRequest('/send_code', 'POST', { phone });
                if (result.success) {
                    addMessage(`验证码已发送到 ${phone}`);
                } else {
                    addMessage(`发送失败: ${result.error}`);
                }
            } catch (error) {
                addMessage(`发送验证码失败: ${error.message}`);
            }
        });
        
        document.getElementById('verifyBtn').addEventListener('click', async () => {
            const phone = document.getElementById('phone').value.trim();
            const code = document.getElementById('code').value.trim();
            if (!phone || !code) return alert('请输入手机号和验证码');
            
            try {
                const result = await makeRequest('/verify', 'POST', { phone, code });
                if (result.success) {
                    addMessage('登录成功！');
                    document.getElementById('code').value = '';
                } else {
                    addMessage(`登录失败: ${result.error}`);
                }
            } catch (error) {
                addMessage(`登录失败: ${error.message}`);
            }
        });
        
        document.getElementById('sendBtn').addEventListener('click', async () => {
            const recipient = document.getElementById('recipient').value.trim();
            const message = document.getElementById('messageText').value.trim();
            if (!recipient || !message) return alert('请输入收件人和消息内容');
            
            try {
                const result = await makeRequest('/send', 'POST', { username: recipient, message });
                if (result.success) {
                    addMessage(`发送给 ${recipient}: ${message}`, 'sent');
                    document.getElementById('messageText').value = '';
                }
            } catch (error) {
                addMessage(`发送失败: ${error.message}`);
            }
        });
        
        document.getElementById('getUserInfoBtn').addEventListener('click', async () => {
            try {
                const result = await makeRequest('/me');
                if (result.id) {
                    addMessage(`用户信息: ${result.first_name} (@${result.username}) - ${result.phone}`);
                }
            } catch (error) {
                addMessage(`获取用户信息失败: ${error.message}`);
            }
        });
    </script>
</body>
</html>
EOF

# 6. 创建主页
cat > index.html << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram多会话客户端系统</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 600px;
        }
        .btn {
            display: inline-block;
            padding: 15px 30px;
            margin: 10px;
            background: #2196F3;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #1976D2;
            transform: translateY(-2px);
        }
        .info {
            background: #f0f8ff;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Telegram多会话客户端系统</h1>
        
        <div class="info">
            <h3>📱 移动设备访问</h3>
            <p>服务器地址: <strong>http://$SERVER_IP</strong></p>
        </div>
        
        <div>
            <a href="telegram_web_client.html" class="btn">🌐 Web客户端</a>
        </div>
        
        <div style="margin-top: 30px; font-size: 14px; color: #666;">
            <p>API后端: <a href="/debug/session" target="_blank">测试API</a></p>
        </div>
    </div>
</body>
</html>
EOF

# 7. 配置Nginx
echo "🌐 配置Nginx..."
sudo tee /etc/nginx/sites-available/telegram-client << EOF
server {
    listen 80;
    server_name _;
    
    root ~/telegram-client;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ @backend;
    }
    
    location @backend {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location ~ \.(html|css|js|png|jpg|gif|ico|svg)$ {
        expires 1h;
        add_header Cache-Control "public";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/telegram-client /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# 8. 启动服务
echo "🚀 启动服务..."

# 启动API后端
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
API_PID=$!
echo $API_PID > api.pid

# 等待服务启动
sleep 5

# 检查服务状态
if kill -0 $API_PID 2>/dev/null; then
    echo "✅ API后端启动成功 (PID: $API_PID)"
else
    echo "❌ API后端启动失败"
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx运行正常"
else
    echo "❌ Nginx启动失败"
fi

echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""
echo "📱 访问地址："
echo "   http://$SERVER_IP"
echo "   http://$SERVER_IP/telegram_web_client.html"
echo ""
echo "🔧 管理命令："
echo "   查看API日志: tail -f ~/telegram-client/api.log"
echo "   停止API: kill \$(cat ~/telegram-client/api.pid)"
echo "   重启Nginx: sudo systemctl restart nginx"
echo ""
echo "📋 使用说明："
echo "1. 在手机浏览器中访问上述地址"
echo "2. 输入子域名（如：user1）"
echo "3. 完成Telegram登录"
echo "4. 开始使用客户端"
echo "=========================================="