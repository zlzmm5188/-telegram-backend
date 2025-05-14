
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from telethon.sync import TelegramClient

import os

app = FastAPI()

# === 添加 CORS 中间件 ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telegram 配置
API_ID = 27941788
API_HASH = '0cd0979dc85b2433a7648342e7fce258'
SESSION_FILE = "session.session"

class PhoneModel(BaseModel):
    phone: str

class VerifyModel(BaseModel):
    phone: str
    code: str

class SendModel(BaseModel):
    username: str
    message: str

@app.post("/send_code")
def send_code(data: PhoneModel):
    with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
        client.send_code_request(data.phone)
    return {"success": True, "msg": "Code sent"}

@app.post("/verify")
def verify(data: VerifyModel):
    try:
        with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
            client.sign_in(data.phone, data.code)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

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

@app.post("/send")
def send(data: SendModel):
    try:
        with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
            client.send_message(data.username, data.message)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
