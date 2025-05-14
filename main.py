
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from telethon import TelegramClient

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
async def send_code(data: PhoneModel):
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(data.phone)
        await client.disconnect()
        return {"success": True, "msg": "Code sent"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/verify")
async def verify(data: VerifyModel):
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.connect()
        await client.sign_in(data.phone, data.code)
        await client.disconnect()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/me")
async def me():
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        me = await client.get_me()
        await client.disconnect()
        return {
            "id": me.id,
            "first_name": me.first_name,
            "username": me.username,
            "phone": me.phone
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/send")
async def send(data: SendModel):
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        await client.send_message(data.username, data.message)
        await client.disconnect()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
