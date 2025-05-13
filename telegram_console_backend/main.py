
from fastapi import FastAPI, Request
from pydantic import BaseModel
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

app = FastAPI()

# ====== 请替换为你的 Telegram API 凭证 ======
API_ID = 27941788
API_HASH = '0cd0979dc85b2433a7648342e7fce258'
SESSION_FILE = "session.session"

# 请求模型
class PhoneModel(BaseModel):
    phone: str

class VerifyModel(BaseModel):
    phone: str
    code: str

class SendModel(BaseModel):
    username: str
    message: str

# 发送验证码
@app.post("/send_code")
def send_code(data: PhoneModel):
    with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
        client.send_code_request(data.phone)
    return {"success": True, "msg": "Code sent"}

# 输入验证码登录
@app.post("/verify")
def verify(data: VerifyModel):
    try:
        with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
            client.sign_in(data.phone, data.code)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 获取当前账号信息
@app.get("/me")
def me():
    with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
        me = client.get_me()
        return {
            "id": me.id,
            "first_name": me.first_name,
            "username": me.username,
            "phone": me.phone
        }

# 发送消息
@app.post("/send")
def send(data: SendModel):
    try:
        with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
            client.send_message(data.username, data.message)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
