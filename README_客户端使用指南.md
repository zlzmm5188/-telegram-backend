# 🚀 Telegram多会话客户端系统使用指南

## 📋 系统概述

这是一个完整的Telegram多会话管理系统，解决了传统客户端会话冲突导致的掉号问题。系统包含：

1. **FastAPI后端** - 处理Telegram API调用和会话管理
2. **Telegram-TT客户端** - 现代化的Web Telegram客户端
3. **多会话启动器** - 管理多个独立的客户端实例
4. **Web客户端** - 简化的浏览器内客户端

## 🔧 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  启动器界面     │───▶│   FastAPI后端    │───▶│  Telegram API   │
│  (管理多会话)   │    │  (会话管理)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Telegram-TT #1  │    │ Telegram-TT #2   │    │ Telegram-TT #N  │
│ (user1会话)     │    │ (user2会话)      │    │ (userN会话)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 1. 启动系统服务

确保以下服务正在运行：

```bash
# 1. 启动FastAPI后端 (端口8000)
cd /workspace
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# 2. 启动Telegram-TT (端口3000)
cd /workspace/telegram-tt
npm run dev &
```

### 2. 打开启动器界面

在浏览器中打开：
```
file:///workspace/telegram-tt-launcher.html
```

## 📱 使用步骤

### 第一步：登录Telegram账号

1. 在启动器中输入子域名（例如：`user1`）
2. 点击"⚡ 快速登录"
3. 输入手机号（格式：+8613800138000）
4. 输入收到的验证码
5. 等待"登录成功"提示

### 第二步：启动客户端

1. 确认子域名已登录（点击"🔍 检查API状态"）
2. 点击"🚀 启动新会话"
3. 新的Telegram-TT窗口将打开
4. 客户端会自动连接到对应的会话

### 第三步：管理多个会话

- **创建更多会话**：重复上述步骤，使用不同的子域名
- **切换会话**：在启动器中点击"🔍 切换到此会话"
- **关闭会话**：点击"❌ 关闭"按钮

## 🎯 核心特性

### ✅ 会话隔离
- 每个子域名使用独立的session文件
- 不同会话完全隔离，不会相互影响
- 支持同时登录多个Telegram账号

### ✅ 现代化界面
- 基于Telegram-TT，官方认证的客户端
- 支持所有Telegram功能：消息、媒体、群组等
- 响应式设计，支持桌面和移动设备

### ✅ 智能管理
- 实时监控会话状态
- 自动检测窗口关闭
- 支持会话重启和恢复

## 🔧 高级功能

### 多种客户端选择

1. **Telegram-TT** (推荐)
   - 功能最完整
   - 性能最佳
   - 官方认证

2. **Web客户端**
   - 轻量级
   - 基本功能
   - 适合简单使用

### API接口

系统提供完整的REST API：

```bash
# 检查会话状态
curl -H "Host: user1.example.com" http://localhost:8000/session/status

# 发送验证码
curl -X POST -H "Host: user1.example.com" -H "Content-Type: application/json" \
  -d '{"phone":"+8613800138000"}' http://localhost:8000/send_code

# 验证登录
curl -X POST -H "Host: user1.example.com" -H "Content-Type: application/json" \
  -d '{"phone":"+8613800138000","code":"12345"}' http://localhost:8000/verify

# 发送消息
curl -X POST -H "Host: user1.example.com" -H "Content-Type: application/json" \
  -d '{"username":"@someone","message":"Hello"}' http://localhost:8000/send

# 获取用户信息
curl -H "Host: user1.example.com" http://localhost:8000/me
```

## 📁 文件结构

```
/workspace/
├── main.py                          # FastAPI后端
├── requirements.txt                 # Python依赖
├── telegram-tt/                     # Telegram-TT客户端
│   ├── .env                        # 环境配置
│   └── ...                         # 客户端源码
├── telegram-tt-launcher.html       # 多会话启动器
├── telegram_web_client.html        # Web客户端
├── telegram_client_gui.py          # GUI客户端（可选）
└── telegram_client_cli.py          # 命令行客户端（可选）
```

## 🛠️ 故障排除

### 常见问题

1. **客户端无法连接**
   - 检查API服务是否运行：`curl http://localhost:8000/debug/session`
   - 确认已完成Telegram登录
   - 检查子域名是否正确

2. **会话冲突**
   - 确保每个账号使用不同的子域名
   - 不要同时在多个地方使用相同的子域名

3. **验证码收不到**
   - 检查手机号格式是否正确（+8613800138000）
   - 确认网络连接正常
   - 尝试重新发送验证码

### 调试模式

启用详细日志：

```bash
# 后端调试
cd /workspace
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# 前端调试
# 在浏览器中打开开发者工具查看控制台日志
```

## 🔐 安全注意事项

1. **API密钥保护**
   - 不要在公共环境中暴露API_ID和API_HASH
   - 定期检查.env文件的权限

2. **会话文件安全**
   - session_*.session文件包含登录凭据
   - 不要共享或上传这些文件

3. **网络安全**
   - 在生产环境中使用HTTPS
   - 配置适当的CORS策略

## 📊 监控和维护

### 会话文件管理

```bash
# 查看所有会话文件
ls -la /workspace/session_*.session

# 清理过期会话
find /workspace -name "session_*.session" -mtime +30 -delete
```

### 系统监控

启动器界面提供实时监控：
- 会话状态
- 连接数量  
- 系统日志
- 错误报告

## 🎉 总结

这个系统彻底解决了Telegram客户端的会话冲突问题：

- ✅ **多账号支持** - 同时管理多个Telegram账号
- ✅ **会话隔离** - 每个账号独立运行，互不干扰
- ✅ **现代界面** - 基于官方认证的Telegram-TT
- ✅ **易于管理** - 可视化的会话管理界面
- ✅ **API集成** - 完整的REST API支持

现在您可以：
1. 同时登录多个Telegram账号
2. 每个账号使用独立的客户端窗口
3. 不用担心掉号问题
4. 轻松管理和切换不同会话

享受无冲突的Telegram多账号体验！🎊