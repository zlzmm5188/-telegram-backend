#!/usr/bin/env python3
"""
Telegram客户端 - 图形界面版本
支持多子域名会话管理
"""

import asyncio
import hashlib
import requests
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from telethon import TelegramClient
from telethon.events import NewMessage
import json
import os
from datetime import datetime

# 配置
API_ID = 27941788
API_HASH = '0cd0979dc85b2433a7648342e7fce258'
BASE_URL = "http://localhost:8000"

class TelegramClientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Telegram客户端")
        self.root.geometry("800x600")
        
        self.client = None
        self.subdomain = None
        self.session_file = None
        self.is_connected = False
        self.message_loop_task = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 连接部分
        connect_frame = ttk.LabelFrame(main_frame, text="连接设置", padding="5")
        connect_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(connect_frame, text="子域名:").grid(row=0, column=0, sticky=tk.W)
        self.subdomain_var = tk.StringVar(value="user1")
        subdomain_entry = ttk.Entry(connect_frame, textvariable=self.subdomain_var, width=20)
        subdomain_entry.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)
        
        self.connect_button = ttk.Button(connect_frame, text="连接", command=self.connect_client)
        self.connect_button.grid(row=0, column=2, padx=(10, 0))
        
        self.disconnect_button = ttk.Button(connect_frame, text="断开", command=self.disconnect_client, state='disabled')
        self.disconnect_button.grid(row=0, column=3, padx=(5, 0))
        
        # 状态显示
        self.status_label = ttk.Label(connect_frame, text="状态: 未连接", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # 消息显示区域
        message_frame = ttk.LabelFrame(main_frame, text="消息", padding="5")
        message_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.message_text = scrolledtext.ScrolledText(message_frame, height=20, width=70)
        self.message_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 发送消息部分
        send_frame = ttk.LabelFrame(main_frame, text="发送消息", padding="5")
        send_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(send_frame, text="收件人:").grid(row=0, column=0, sticky=tk.W)
        self.recipient_var = tk.StringVar()
        recipient_entry = ttk.Entry(send_frame, textvariable=self.recipient_var, width=30)
        recipient_entry.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)
        
        ttk.Label(send_frame, text="消息:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.message_var = tk.StringVar()
        message_entry = ttk.Entry(send_frame, textvariable=self.message_var, width=50)
        message_entry.grid(row=1, column=1, padx=(5, 0), sticky=(tk.W, tk.E), pady=(5, 0))
        message_entry.bind('<Return>', self.send_message)
        
        send_button = ttk.Button(send_frame, text="发送", command=self.send_message)
        send_button.grid(row=1, column=2, padx=(10, 0), pady=(5, 0))
        
        # 功能按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="检查API状态", command=self.check_api_status).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="获取用户信息", command=self.get_user_info).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="清空消息", command=self.clear_messages).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="手动登录", command=self.manual_login).grid(row=0, column=3, padx=(0, 5))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        message_frame.columnconfigure(0, weight=1)
        message_frame.rowconfigure(0, weight=1)
        send_frame.columnconfigure(1, weight=1)
        
    def log_message(self, message):
        """在消息区域显示日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.message_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.message_text.see(tk.END)
        self.root.update()
        
    def get_session_file(self, subdomain):
        """根据子域名生成session文件名"""
        session_id = hashlib.md5(subdomain.encode()).hexdigest()[:8]
        return f"session_{session_id}.session"
    
    def check_api_status(self):
        """检查API状态"""
        try:
            subdomain = self.subdomain_var.get().strip()
            if not subdomain:
                messagebox.showerror("错误", "请输入子域名")
                return
                
            headers = {"Host": f"{subdomain}.example.com"}
            response = requests.get(f"{BASE_URL}/session/status", headers=headers, timeout=5)
            data = response.json()
            
            if data.get("authorized"):
                user = data.get("user", {})
                message = f"API状态: 已授权\n用户: {user.get('first_name')} (@{user.get('username')})\n电话: {user.get('phone')}"
                self.log_message(message)
            else:
                self.log_message(f"API状态: 未授权 - {data.get('reason', '未知原因')}")
                
        except Exception as e:
            self.log_message(f"检查API状态失败: {e}")
    
    def manual_login(self):
        """手动登录流程"""
        subdomain = self.subdomain_var.get().strip()
        if not subdomain:
            messagebox.showerror("错误", "请输入子域名")
            return
            
        phone = simpledialog.askstring("登录", "请输入手机号:")
        if not phone:
            return
            
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
                code = simpledialog.askstring("验证", "请输入收到的验证码:")
                if not code:
                    return
                    
                # 验证登录
                response = requests.post(f"{BASE_URL}/verify",
                                       json={"phone": phone, "code": code},
                                       headers=headers)
                result = response.json()
                
                if result.get("success"):
                    self.log_message(f"登录成功! Session文件: {result.get('session_file')}")
                    messagebox.showinfo("成功", "登录成功! 现在可以连接客户端了")
                else:
                    self.log_message(f"登录失败: {result.get('error')}")
            else:
                self.log_message(f"发送验证码失败: {result.get('error')}")
                
        except Exception as e:
            self.log_message(f"登录流程失败: {e}")
    
    def connect_client(self):
        """连接客户端"""
        subdomain = self.subdomain_var.get().strip()
        if not subdomain:
            messagebox.showerror("错误", "请输入子域名")
            return
            
        self.subdomain = subdomain
        self.session_file = self.get_session_file(subdomain)
        
        def connect_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._connect_client_async())
            
        thread = threading.Thread(target=connect_async)
        thread.daemon = True
        thread.start()
    
    async def _connect_client_async(self):
        """异步连接客户端"""
        try:
            self.root.after(0, lambda: self.log_message(f"正在连接到子域名: {self.subdomain}"))
            self.root.after(0, lambda: self.log_message(f"使用Session文件: {self.session_file}"))
            
            # 创建客户端
            self.client = TelegramClient(self.session_file, API_ID, API_HASH)
            await self.client.start()
            
            # 获取用户信息
            me = await self.client.get_me()
            self.root.after(0, lambda: self.log_message(f"连接成功! 用户: {me.first_name} (@{me.username})"))
            
            # 更新UI状态
            self.is_connected = True
            self.root.after(0, self._update_connection_status, True)
            
            # 设置消息监听
            @self.client.on(NewMessage)
            async def message_handler(event):
                sender = await event.get_sender()
                message = f"收到消息来自 {sender.first_name}: {event.message.text}"
                self.root.after(0, lambda: self.log_message(message))
            
            # 保持连接
            self.root.after(0, lambda: self.log_message("开始监听消息..."))
            await self.client.run_until_disconnected()
            
        except Exception as e:
            error_msg = f"连接失败: {e}"
            self.root.after(0, lambda: self.log_message(error_msg))
            self.root.after(0, lambda: messagebox.showerror("连接失败", f"{error_msg}\n\n请确保已通过'手动登录'完成Telegram登录"))
            self.root.after(0, self._update_connection_status, False)
    
    def _update_connection_status(self, connected):
        """更新连接状态"""
        if connected:
            self.status_label.config(text=f"状态: 已连接 ({self.subdomain})", foreground="green")
            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')
        else:
            self.status_label.config(text="状态: 未连接", foreground="red")
            self.connect_button.config(state='normal')
            self.disconnect_button.config(state='disabled')
            self.is_connected = False
    
    def disconnect_client(self):
        """断开客户端连接"""
        def disconnect_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._disconnect_client_async())
            
        thread = threading.Thread(target=disconnect_async)
        thread.daemon = True
        thread.start()
    
    async def _disconnect_client_async(self):
        """异步断开连接"""
        try:
            if self.client:
                await self.client.disconnect()
                self.root.after(0, lambda: self.log_message("客户端已断开连接"))
            self.root.after(0, self._update_connection_status, False)
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"断开连接时出错: {e}"))
    
    def send_message(self, event=None):
        """发送消息"""
        if not self.is_connected:
            messagebox.showwarning("警告", "请先连接客户端")
            return
            
        recipient = self.recipient_var.get().strip()
        message = self.message_var.get().strip()
        
        if not recipient or not message:
            messagebox.showwarning("警告", "请输入收件人和消息内容")
            return
        
        def send_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._send_message_async(recipient, message))
            
        thread = threading.Thread(target=send_async)
        thread.daemon = True
        thread.start()
        
        # 清空消息输入框
        self.message_var.set("")
    
    async def _send_message_async(self, recipient, message):
        """异步发送消息"""
        try:
            if self.client:
                await self.client.send_message(recipient, message)
                self.root.after(0, lambda: self.log_message(f"消息已发送给 {recipient}: {message}"))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"发送消息失败: {e}"))
    
    def get_user_info(self):
        """获取用户信息"""
        if not self.is_connected:
            messagebox.showwarning("警告", "请先连接客户端")
            return
            
        def get_info_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._get_user_info_async())
            
        thread = threading.Thread(target=get_info_async)
        thread.daemon = True
        thread.start()
    
    async def _get_user_info_async(self):
        """异步获取用户信息"""
        try:
            if self.client:
                me = await self.client.get_me()
                info = f"用户信息:\nID: {me.id}\n姓名: {me.first_name}\n用户名: @{me.username}\n电话: {me.phone}"
                self.root.after(0, lambda: self.log_message(info))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"获取用户信息失败: {e}"))
    
    def clear_messages(self):
        """清空消息显示"""
        self.message_text.delete(1.0, tk.END)
    
    def run(self):
        """运行客户端"""
        self.log_message("Telegram客户端已启动")
        self.log_message("使用步骤:")
        self.log_message("1. 输入子域名 (例如: user1)")
        self.log_message("2. 点击'手动登录'完成Telegram登录")
        self.log_message("3. 点击'连接'启动客户端")
        self.log_message("4. 开始发送和接收消息")
        self.log_message("-" * 50)
        
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = TelegramClientGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序运行出错: {e}")