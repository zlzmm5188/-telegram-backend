from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import LoginRequest, LoginResponse, User as UserSchema
from ..crud import get_user_by_username
from ..auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 验证用户
    user = get_user_by_username(db, request.username)
    if not user or not verify_password(request.password, user.password):
        return LoginResponse(
            success=False,
            message="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    # 转换用户信息
    user_data = UserSchema.from_orm(user)
    
    return LoginResponse(
        success=True,
        token=access_token,
        user=user_data,
        message="登录成功"
    )


@router.post("/logout")
def logout(current_user: UserSchema = Depends(get_current_user)):
    """用户登出"""
    return {"success": True, "message": "登出成功"}


@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: UserSchema = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user