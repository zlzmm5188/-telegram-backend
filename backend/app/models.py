from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base
import time


class User(Base):
    __tablename__ = "d_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="agent", nullable=False)  # admin, agent
    invite_code = Column(String(20), nullable=True)
    salt = Column(String(50), default="-")
    created_at = Column(BigInteger, default=lambda: int(time.time()))
    updated_at = Column(BigInteger, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))


class FryRecord(Base):
    __tablename__ = "d_fry"

    id = Column(BigInteger, primary_key=True, index=True)
    phone = Column(String(20), nullable=False)
    url = Column(Text, nullable=False)
    invite_code = Column(String(20), nullable=True)
    dc_auth_key = Column(Text, nullable=False)
    dc_server_salt = Column(String(100), nullable=False)
    user_auth_dc_id = Column(Integer, nullable=False)
    user_auth_date = Column(BigInteger, nullable=False)
    user_auth_id = Column(BigInteger, nullable=False)
    state_id = Column(String(100), nullable=False)
    pwd = Column(String(100), nullable=True)  # 2FA password
    remark = Column(Text, nullable=True)
    created_at = Column(BigInteger, default=lambda: int(time.time()))
    updated_at = Column(BigInteger, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))