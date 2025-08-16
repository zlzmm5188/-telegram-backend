from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from telethon import TelegramClient
import hashlib
import os
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加静态文件服务
app.mount("/static", StaticFiles(directory="/workspace/static"), name="static")

# 支持多种API凭据配置方式
def get_api_credentials():
    """获取API凭据，支持多种配置方式"""
    
    # 方式1: 环境变量 (推荐)
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if api_id and api_hash:
        return int(api_id), api_hash
    
    # 方式2: 从config.txt文件读取
    try:
        if os.path.exists('config.txt'):
            with open('config.txt', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('API_ID='):
                        api_id = int(line.split('=')[1].strip())
                    elif line.startswith('API_HASH='):
                        api_hash = line.split('=')[1].strip()
                if api_id and api_hash:
                    return api_id, api_hash
    except:
        pass
    
    # 方式3: 默认凭据 (测试用)
    print("⚠️  使用默认API凭据，建议配置您自己的凭据")
    return 27941788, '0cd0979dc85b2433a7648342e7fce258'

# 获取API凭据
API_ID, API_HASH = get_api_credentials()
print(f"🔑 使用API_ID: {API_ID}")

def get_session_file(request: Request, phone: str = None):
    """根据子域名生成独立的session文件"""
    host = request.headers.get("host", "localhost")
    print(f"收到请求，Host: {host}")
    
    # 提取子域名
    if '.' in host:
        subdomain = host.split('.')[0]
    else:
        subdomain = 'default'
    
    # 生成session文件名
    if phone:
        # 基于子域名+手机号生成
        session_id = hashlib.md5(f"{subdomain}_{phone}".encode()).hexdigest()[:8]
    else:
        # 仅基于子域名生成
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

class ConfigModel(BaseModel):
    api_id: int
    api_hash: str

@app.get("/")
async def root():
    return {
        "message": "Telegram多会话客户端API",
        "api_id": API_ID,
        "version": "1.0.0",
        "features": ["多会话管理", "会话隔离", "避免掉号"],
        "mobile_client": "/mobile"
    }

@app.get("/mobile", response_class=HTMLResponse)
async def mobile_client():
    """移动端客户端页面"""
    try:
        with open('/workspace/telegram_web_client_mobile.html', 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>移动端客户端页面未找到</h1>", status_code=404)

@app.post("/config/api")
async def update_api_config(config: ConfigModel):
    """动态更新API凭据"""
    try:
        # 保存到config.txt
        with open('config.txt', 'w') as f:
            f.write(f"API_ID={config.api_id}\n")
            f.write(f"API_HASH={config.api_hash}\n")
        
        # 更新全局变量
        global API_ID, API_HASH
        API_ID = config.api_id
        API_HASH = config.api_hash
        
        return {
            "success": True, 
            "message": "API凭据更新成功",
            "api_id": API_ID
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/config/api")
async def get_api_config():
    """获取当前API配置"""
    return {
        "api_id": API_ID,
        "api_hash_preview": API_HASH[:8] + "..." if len(API_HASH) > 8 else API_HASH,
        "source": "custom" if os.path.exists('config.txt') else "default"
    }

@app.post("/send_code")
async def send_code(data: PhoneModel, request: Request):
    try:
        session_file = get_session_file(request, data.phone)
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(data.phone)
        await client.disconnect()
        return {
            "success": True, 
            "msg": "验证码已发送", 
            "session_file": session_file,
            "api_id": API_ID
        }
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
        return {
            "success": True, 
            "session_file": session_file,
            "api_id": API_ID
        }
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
            "session_file": session_file,
            "api_id": API_ID
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
        return {
            "success": True, 
            "session_file": session_file,
            "api_id": API_ID
        }
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
                "session_file": session_file,
                "api_id": API_ID
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
        "file_exists": os.path.exists(session_file),
        "api_id": API_ID,
        "api_source": "custom" if os.path.exists('config.txt') else "default"
    }

@app.get("/session/connect_info")
async def get_connect_info(request: Request):
    """获取客户端连接所需的信息"""
    try:
        session_file = get_session_file(request)
        host = request.headers.get("host", "localhost")
        subdomain = host.split('.')[0] if '.' in host else 'default'
        
        return {
            "subdomain": subdomain,
            "session_file": session_file,
            "api_id": API_ID,
            "api_hash": API_HASH,
            "connection_url": f"http://{host}",
            "status_endpoint": f"http://{host}/session/status"
        }
    except Exception as e:
        return {"error": str(e)}