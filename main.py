
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from telethon.sync import TelegramClient

app = FastAPI()

# 启用 CORS
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
def send_code(data: PhoneModel):
    try:
        with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
            client.send_code_request(data.phone)
        return {"success": True, "msg": "Code sent"}
    except Exception as e:
        return {"success": False, "error": str(e)}

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
