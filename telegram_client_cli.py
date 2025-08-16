#!/usr/bin/env python3
"""
Telegram客户端 - 命令行版本
支持多子域名会话管理
"""

import asyncio
import hashlib
import requests
from telethon import TelegramClient
from telethon.events import NewMessage
import json
import os
from datetime import datetime

# 配置
API_ID = 27941788
API_HASH = '0cd0979dc85b2433a7648342e7fce258'
BASE_URL = "http://localhost:8000"

class TelegramClientCLI:
    def __init__(self):
        self.client = None
        self.subdomain = None
        self.session_file = None
        self.is_connected = False
        
    def log_message(self, message):
        """打印日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def get_session_file(self, subdomain):
        """根据子域名生成session文件名"""
        session_id = hashlib.md5(subdomain.encode()).hexdigest()[:8]
        return f"session_{session_id}.session"
    
    def check_api_status(self, subdomain):
        """检查API状态"""
        try:
            headers = {"Host": f"{subdomain}.example.com"}
            response = requests.get(f"{BASE_URL}/session/status", headers=headers, timeout=5)
            data = response.json()
            
            if data.get("authorized"):
                user = data.get("user", {})
                self.log_message(f"API状态: 已授权")
                self.log_message(f"用户: {user.get('first_name')} (@{user.get('username')})")
                self.log_message(f"电话: {user.get('phone')}")
                return True
            else:
                self.log_message(f"API状态: 未授权 - {data.get('reason', '未知原因')}")
                return False
                
        except Exception as e:
            self.log_message(f"检查API状态失败: {e}")
            return False
    
    def manual_login(self, subdomain):
        """手动登录流程"""
        phone = input("请输入手机号: ").strip()
        if not phone:
            self.log_message("手机号不能为空")
            return False
            
        try:
            # 发送验证码
            headers = {"Host": f"{subdomain}.example.com"}
            response = requests.post(f"{BASE_URL}/send_code", 
                                   json={"phone": phone}, 
                                   headers=headers)
            result = response.json()
            
            if result.get("success"):
                self.log_message(f"验证码已发送到 {phone}")
                
                # 获取验证码
                code = input("请输入收到的验证码: ").strip()
                if not code:
                    self.log_message("验证码不能为空")
                    return False
                    
                # 验证登录
                response = requests.post(f"{BASE_URL}/verify",
                                       json={"phone": phone, "code": code},
                                       headers=headers)
                result = response.json()
                
                if result.get("success"):
                    self.log_message(f"登录成功! Session文件: {result.get('session_file')}")
                    return True
                else:
                    self.log_message(f"登录失败: {result.get('error')}")
                    return False
            else:
                self.log_message(f"发送验证码失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.log_message(f"登录流程失败: {e}")
            return False
    
    async def connect_client(self, subdomain):
        """连接客户端"""
        try:
            self.subdomain = subdomain
            self.session_file = self.get_session_file(subdomain)
            
            self.log_message(f"正在连接到子域名: {subdomain}")
            self.log_message(f"使用Session文件: {self.session_file}")
            
            # 创建客户端
            self.client = TelegramClient(self.session_file, API_ID, API_HASH)
            await self.client.start()
            
            # 获取用户信息
            me = await self.client.get_me()
            self.log_message(f"连接成功! 用户: {me.first_name} (@{me.username})")
            
            self.is_connected = True
            
            # 设置消息监听
            @self.client.on(NewMessage)
            async def message_handler(event):
                sender = await event.get_sender()
                self.log_message(f"收到消息来自 {sender.first_name}: {event.message.text}")
            
            return True
            
        except Exception as e:
            self.log_message(f"连接失败: {e}")
            self.log_message("请确保已完成Telegram登录")
            return False
    
    async def send_message(self, recipient, message):
        """发送消息"""
        if not self.is_connected or not self.client:
            self.log_message("客户端未连接")
            return False
            
        try:
            await self.client.send_message(recipient, message)
            self.log_message(f"消息已发送给 {recipient}: {message}")
            return True
        except Exception as e:
            self.log_message(f"发送消息失败: {e}")
            return False
    
    async def get_user_info(self):
        """获取用户信息"""
        if not self.is_connected or not self.client:
            self.log_message("客户端未连接")
            return
            
        try:
            me = await self.client.get_me()
            self.log_message("=" * 40)
            self.log_message("用户信息:")
            self.log_message(f"ID: {me.id}")
            self.log_message(f"姓名: {me.first_name}")
            self.log_message(f"用户名: @{me.username}")
            self.log_message(f"电话: {me.phone}")
            self.log_message("=" * 40)
        except Exception as e:
            self.log_message(f"获取用户信息失败: {e}")
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.disconnect()
            self.log_message("客户端已断开连接")
            self.is_connected = False
    
    async def run_interactive(self):
        """运行交互式界面"""
        self.log_message("开始监听消息...")
        self.log_message("输入命令:")
        self.log_message("  send <用户名> <消息>  - 发送消息")
        self.log_message("  info                 - 获取用户信息")
        self.log_message("  quit                 - 退出")
        self.log_message("-" * 50)
        
        # 在后台运行客户端
        client_task = asyncio.create_task(self.client.run_until_disconnected())
        
        # 处理用户输入
        try:
            while True:
                try:
                    command = await asyncio.get_event_loop().run_in_executor(
                        None, input, "请输入命令: "
                    )
                    command = command.strip()
                    
                    if command == "quit":
                        break
                    elif command == "info":
                        await self.get_user_info()
                    elif command.startswith("send "):
                        parts = command.split(" ", 2)
                        if len(parts) >= 3:
                            recipient = parts[1]
                            message = parts[2]
                            await self.send_message(recipient, message)
                        else:
                            self.log_message("用法: send <用户名> <消息>")
                    else:
                        self.log_message("未知命令. 可用命令: send, info, quit")
                        
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
                    
        finally:
            client_task.cancel()
            await self.disconnect()

async def main():
    """主函数"""
    client = TelegramClientCLI()
    
    print("=" * 60)
    print("    Telegram客户端 - 命令行版本")
    print("=" * 60)
    
    # 获取子域名
    subdomain = input("请输入子域名 (例如: user1): ").strip()
    if not subdomain:
        subdomain = "user1"
        
    client.log_message(f"使用子域名: {subdomain}")
    
    # 检查API状态
    client.log_message("检查API状态...")
    if not client.check_api_status(subdomain):
        choice = input("需要先登录吗? (y/n): ").strip().lower()
        if choice == 'y':
            if not client.manual_login(subdomain):
                client.log_message("登录失败，退出程序")
                return
        else:
            client.log_message("跳过登录，尝试直接连接...")
    
    # 连接客户端
    client.log_message("正在连接客户端...")
    if await client.connect_client(subdomain):
        client.log_message("客户端连接成功!")
        await client.run_interactive()
    else:
        client.log_message("客户端连接失败")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序运行出错: {e}")