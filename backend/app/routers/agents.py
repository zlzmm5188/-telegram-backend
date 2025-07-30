from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..schemas import User as UserSchema, UserCreate, ApiResponse
from ..crud import get_users, create_user, delete_user, get_user_by_username
from ..auth import get_current_admin_user
from ..models import User

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("")
def get_agents_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取代理列表（仅管理员）"""
    # 计算偏移量
    skip = (page - 1) * pageSize
    
    # 获取代理用户
    agents, total = get_users(
        db=db,
        skip=skip,
        limit=pageSize,
        username=username,
        role="agent"
    )
    
    return {
        "success": True,
        "data": agents,
        "total": total
    }


@router.post("", response_model=ApiResponse)
def create_agent(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建代理（仅管理员）"""
    # 检查用户名是否已存在
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        return {
            "success": False,
            "message": "用户名已存在"
        }
    
    # 设置角色为代理
    user_data.role = "agent"
    
    # 创建用户
    try:
        new_user = create_user(db=db, user=user_data)
        return {
            "success": True,
            "data": new_user,
            "message": "代理创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建失败: {str(e)}")


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除代理（仅管理员）"""
    # 不能删除管理员账户
    user_to_delete = db.query(User).filter(User.id == agent_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user_to_delete.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员账户")
    
    success = delete_user(db=db, user_id=agent_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"success": True, "message": "删除成功"}