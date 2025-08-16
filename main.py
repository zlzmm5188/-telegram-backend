
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from telethon import TelegramClient
import hashlib

app = FastAPI()

# 启用 CORS 支持
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
    """根据子域名生成独立的session文件"""
    host = request.headers.get("host", "localhost")
    print(f"收到请求，Host: {host}")  # 调试信息
    
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
    print(f"使用session文件: {session_file}")  # 调试信息
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

# 添加调试端点，查看当前使用的session文件
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
