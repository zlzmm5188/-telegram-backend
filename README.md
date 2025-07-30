# Telegram 管理系统

这是一个基于 React + TypeScript + FastAPI 的现代化 Telegram 管理系统，重新开发了原有的 1.5.0 版本功能。

## 🚀 功能特性

### 前端功能
- 🔐 用户认证（JWT）
- 📊 数据仪表盘
- 👥 代理用户管理  
- 🔍 搜索和过滤
- 📱 响应式设计
- 🎨 现代化 UI（Ant Design）

### 后端功能
- 🛡️ JWT 认证和授权
- 🗄️ SQLite 数据库
- 📝 RESTful API
- 🔒 角色权限控制
- 📊 数据分页和筛选

## 🛠️ 技术栈

### 前端
- **React 18** - 用户界面
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Ant Design** - UI 组件库
- **React Router** - 路由管理
- **Zustand** - 状态管理
- **Axios** - HTTP 客户端

### 后端
- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM
- **SQLite** - 数据库
- **JWT** - 认证
- **Pydantic** - 数据验证

## 📦 项目结构

```
├── src/                    # 前端源码
│   ├── components/         # React 组件
│   ├── pages/             # 页面组件
│   ├── services/          # API 服务
│   ├── stores/            # 状态管理
│   ├── types/             # TypeScript 类型
│   └── main.tsx           # 应用入口
├── backend/               # 后端源码
│   ├── app/               # FastAPI 应用
│   │   ├── routers/       # API 路由
│   │   ├── models.py      # 数据模型
│   │   ├── schemas.py     # Pydantic 模式
│   │   ├── crud.py        # 数据库操作
│   │   ├── auth.py        # 认证逻辑
│   │   └── main.py        # 应用主文件
│   └── run.py             # 启动脚本
├── main.py                # 原有的 Telegram API
└── package.json           # 前端依赖
```

## 🚀 快速开始

### 前端开发

1. **安装依赖**
```bash
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

前端将在 http://localhost:3000 启动

### 后端开发

1. **安装 Python 依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **启动后端服务器**
```bash
python run.py
```

后端将在 http://localhost:8000 启动

### 默认账户

系统会自动创建默认管理员账户：
- **用户名**: admin
- **密码**: admin123

## 🔧 环境变量

### 后端环境变量

可以通过环境变量配置：

```bash
# 数据库URL
DATABASE_URL=sqlite:///./telegram_admin.db

# JWT密钥
SECRET_KEY=your-secret-key

# 默认管理员账户
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 前端环境变量

```bash
# 登录URL（用于 Telegram 登录跳转）
REACT_APP_LOGIN_URL=your-telegram-login-url
```

## 📚 API 文档

后端启动后，可以访问自动生成的 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 权限说明

### 角色权限
- **管理员 (admin)**: 可以管理代理用户，查看所有数据
- **代理 (agent)**: 只能查看自己的数据

### API 权限
- `/auth/*` - 公开接口
- `/dashboard/*` - 需要登录
- `/agents/*` - 仅管理员

## 🗄️ 数据库表结构

### 用户表 (d_user)
```sql
CREATE TABLE d_user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role VARCHAR(20),
    invite_code VARCHAR(20),
    created_at BIGINT,
    updated_at BIGINT
);
```

### 记录表 (d_fry)
```sql
CREATE TABLE d_fry (
    id BIGINT PRIMARY KEY,
    phone VARCHAR(20),
    url TEXT,
    invite_code VARCHAR(20),
    dc_auth_key TEXT,
    dc_server_salt VARCHAR(100),
    user_auth_dc_id INTEGER,
    user_auth_date BIGINT,
    user_auth_id BIGINT,
    state_id VARCHAR(100),
    pwd VARCHAR(100),
    remark TEXT,
    created_at BIGINT,
    updated_at BIGINT
);
```

## 🔗 集成现有系统

本系统可以与您现有的 `main.py` (Telegram API) 配合使用：

1. 保持 `main.py` 运行在 8001 端口
2. 新系统的后端运行在 8000 端口  
3. 前端通过代理访问两个后端

## 🚧 开发计划

- [ ] 集成 Telegram API (`main.py`)
- [ ] 添加数据导入/导出功能
- [ ] 实现实时通知
- [ ] 添加操作日志
- [ ] 部署配置优化

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License