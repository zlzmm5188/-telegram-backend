from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    role: str = "agent"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None


class User(UserBase):
    id: int
    invite_code: Optional[str] = None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class FryRecordBase(BaseModel):
    phone: str
    url: str
    invite_code: Optional[str] = None
    dc_auth_key: str
    dc_server_salt: str
    user_auth_dc_id: int
    user_auth_date: int
    user_auth_id: int
    state_id: str
    pwd: Optional[str] = None
    remark: Optional[str] = None


class FryRecordCreate(FryRecordBase):
    pass


class FryRecordUpdate(BaseModel):
    remark: Optional[str] = None
    pwd: Optional[str] = None


class FryRecord(FryRecordBase):
    id: int
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user: Optional[User] = None
    message: Optional[str] = None


class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    total: Optional[int] = None


class PaginationParams(BaseModel):
    page: int = 1
    pageSize: int = 20


class DashboardSearchParams(PaginationParams):
    date: Optional[str] = None
    phone: Optional[str] = None
    agent: Optional[str] = None


class AgentSearchParams(PaginationParams):
    username: Optional[str] = None