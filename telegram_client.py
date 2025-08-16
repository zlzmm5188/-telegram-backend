#!/usr/bin/env python3
"""
Telegram客户端示例
使用特定子域名的session文件进行连接
"""

import asyncio
import hashlib
import requests
from telethon import TelegramClient
from telethon.events import NewMessage

# 配置
API_ID = 27941788
API_HASH = '0cd0979dc85b2433a7648342e7fce258'

class SubdomainTelegramClient:
    def __init__(self, subdomain: str, base_url: str = "http://localhost:8000"):
        self.subdomain = subdomain
        self.base_url = base_url
        self.session_file = self.get_session_file()
        self.client = None
        
    def get_session_file(self):
        """根据子域名生成session文件名"""
        session_id = hashlib.md5(self.subdomain.encode()).hexdigest()[:8]
        return f"session_{session_id}.session"
    
    async def check_api_status(self):
        """检查API服务器上的session状态"""
        try:
            headers = {"Host": f"{self.subdomain}.example.com"}
            response = requests.get(f"{self.base_url}/session/status", headers=headers)
            return response.json()
        except Exception as e:
            print(f"无法连接到API服务器: {e}")
            return {"authorized": False, "reason": str(e)}
    
    async def get_connect_info(self):
        """获取连接信息"""
        try:
            headers = {"Host": f"{self.subdomain}.example.com"}
            response = requests.get(f"{self.base_url}/session/connect_info", headers=headers)
            return response.json()
        except Exception as e:
            print(f"无法获取连接信息: {e}")
            return {"error": str(e)}
    
    async def start(self):
        """启动客户端"""
        print(f"正在启动客户端，子域名: {self.subdomain}")
        print(f"Session文件: {self.session_file}")
        
        # 检查API状态
        status = await self.check_api_status()
        print(f"API状态: {status}")
        
        # 创建客户端
        self.client = TelegramClient(self.session_file, API_ID, API_HASH)
        
        try:
            await self.client.start()
            
            # 获取当前用户信息
            me = await self.client.get_me()
            print(f"已登录用户: {me.first_name} (@{me.username}) - {me.phone}")
            
            return True
            
        except Exception as e:
            print(f"登录失败: {e}")
            print("请确保已通过API完成登录流程")
            return False
    
    async def send_message(self, username: str, message: str):
        """发送消息"""
        if not self.client:
            print("客户端未启动")
            return False
        
        try:
            await self.client.send_message(username, message)
            print(f"消息已发送给 {username}: {message}")
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    async def listen_for_messages(self):
        """监听新消息"""
        if not self.client:
            print("客户端未启动")
            return
        
        @self.client.on(NewMessage)
        async def message_handler(event):
            sender = await event.get_sender()
            print(f"收到消息来自 {sender.first_name}: {event.message.text}")
        
        print("开始监听消息...")
        await self.client.run_until_disconnected()
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.disconnect()
            print("客户端已断开连接")

# 使用示例
async def main():
    # 选择一个子域名 (对应后台管理界面中的某个用户)
    subdomain = input("请输入子域名 (例如: user1): ").strip() or "user1"
    
    # 创建客户端
    client = SubdomainTelegramClient(subdomain)
    
    # 获取连接信息
    info = await client.get_connect_info()
    print(f"连接信息: {info}")
    
    # 启动客户端
    if await client.start():
        print("\n客户端已成功启动!")
        print("可用命令:")
        print("1. 发送消息: send")
        print("2. 监听消息: listen") 
        print("3. 退出: quit")
        
        while True:
            command = input("\n请输入命令: ").strip().lower()
            
            if command == "send":
                username = input("收件人用户名: ").strip()
                message = input("消息内容: ").strip()
                await client.send_message(username, message)
                
            elif command == "listen":
                print("开始监听消息 (Ctrl+C 停止)...")
                try:
                    await client.listen_for_messages()
                except KeyboardInterrupt:
                    print("\n停止监听")
                    
            elif command == "quit":
                break
                
            else:
                print("无效命令")
        
        await client.disconnect()
    else:
        print("\n客户端启动失败!")
        print(f"请先通过后台管理界面使用子域名 '{subdomain}' 完成Telegram登录")

if __name__ == "__main__":
    asyncio.run(main())