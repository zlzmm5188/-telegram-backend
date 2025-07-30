from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import List, Optional
from .models import User, FryRecord
from .schemas import UserCreate, UserUpdate, FryRecordCreate, FryRecordUpdate
from .auth import get_password_hash
import random
import string
import time
from datetime import datetime


def get_user(db: Session, user_id: int) -> Optional[User]:
    """获取用户"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    """创建用户"""
    # 生成邀请码
    invite_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # 创建用户
    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        role=user.role,
        invite_code=invite_code,
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """更新用户"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    update_data["updated_at"] = int(time.time())
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    username: Optional[str] = None,
    role: Optional[str] = None
) -> tuple[List[User], int]:
    """获取用户列表"""
    query = db.query(User)
    
    # 过滤条件
    if username:
        query = query.filter(User.username.contains(username))
    if role:
        query = query.filter(User.role == role)
    
    # 获取总数
    total = query.count()
    
    # 分页
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return users, total


def get_fry_record(db: Session, record_id: int) -> Optional[FryRecord]:
    """获取记录"""
    return db.query(FryRecord).filter(FryRecord.id == record_id).first()


def create_fry_record(db: Session, record: FryRecordCreate) -> FryRecord:
    """创建记录"""
    db_record = FryRecord(
        **record.dict(),
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_fry_record(db: Session, record_id: int, record: FryRecordUpdate) -> Optional[FryRecord]:
    """更新记录"""
    db_record = db.query(FryRecord).filter(FryRecord.id == record_id).first()
    if not db_record:
        return None
    
    update_data = record.dict(exclude_unset=True)
    update_data["updated_at"] = int(time.time())
    
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


def delete_fry_record(db: Session, record_id: int) -> bool:
    """删除记录"""
    db_record = db.query(FryRecord).filter(FryRecord.id == record_id).first()
    if not db_record:
        return False
    
    db.delete(db_record)
    db.commit()
    return True


def get_fry_records(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    date: Optional[str] = None,
    phone: Optional[str] = None,
    agent: Optional[str] = None
) -> tuple[List[FryRecord], int]:
    """获取记录列表"""
    query = db.query(FryRecord)
    
    # 日期过滤
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            start_timestamp = int(date_obj.timestamp())
            end_timestamp = start_timestamp + 86400  # 一天的秒数
            query = query.filter(
                and_(
                    FryRecord.created_at >= start_timestamp,
                    FryRecord.created_at < end_timestamp
                )
            )
        except ValueError:
            pass  # 忽略无效日期格式
    
    # 手机号过滤
    if phone:
        query = query.filter(FryRecord.phone.contains(phone))
    
    # 代理过滤（通过邀请码）
    if agent:
        agent_user = db.query(User).filter(User.username == agent).first()
        if agent_user and agent_user.invite_code:
            query = query.filter(FryRecord.invite_code == agent_user.invite_code)
    
    # 获取总数
    total = query.count()
    
    # 分页
    records = query.order_by(FryRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return records, total