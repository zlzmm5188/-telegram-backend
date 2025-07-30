from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, dashboard, agents
from .models import User
from .crud import create_user, get_user_by_username
from .schemas import UserCreate
from .database import SessionLocal
import os

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="Telegram Admin API",
    description="Telegram管理系统后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(agents.router)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 创建默认管理员账户
    db = SessionLocal()
    try:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        # 检查是否已存在管理员账户
        existing_admin = get_user_by_username(db, admin_username)
        if not existing_admin:
            admin_user = UserCreate(
                username=admin_username,
                password=admin_password,
                role="admin"
            )
            create_user(db, admin_user)
            print(f"默认管理员账户已创建: {admin_username}/{admin_password}")
        else:
            print("管理员账户已存在")
    finally:
        db.close()


@app.get("/")
def read_root():
    """根路径"""
    return {"message": "Telegram Admin API"}


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)