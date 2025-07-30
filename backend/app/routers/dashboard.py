from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import FryRecord as FryRecordSchema, FryRecordUpdate, ApiResponse
from ..crud import get_fry_records, update_fry_record, delete_fry_record
from ..auth import get_current_user
from ..models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/fry-records")
def get_fry_records_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    date: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    agent: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取记录列表"""
    # 如果不是管理员，只能看到自己代理的记录
    if current_user.role != "admin":
        agent = current_user.username
    
    # 计算偏移量
    skip = (page - 1) * pageSize
    
    # 获取记录
    records, total = get_fry_records(
        db=db,
        skip=skip,
        limit=pageSize,
        date=date,
        phone=phone,
        agent=agent
    )
    
    return {
        "success": True,
        "data": records,
        "total": total
    }


@router.put("/fry-records/{record_id}/remark")
def update_record_remark(
    record_id: int,
    remark_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新记录备注"""
    remark = remark_data.get("remark", "")
    
    # 更新备注
    updated_record = update_fry_record(
        db=db,
        record_id=record_id,
        record=FryRecordUpdate(remark=remark)
    )
    
    if not updated_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return {"success": True, "message": "备注更新成功"}


@router.delete("/fry-records/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除记录"""
    success = delete_fry_record(db=db, record_id=record_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return {"success": True, "message": "删除成功"}