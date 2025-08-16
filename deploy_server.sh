#!/bin/bash
# Telegram多会话客户端系统 - 服务器部署脚本

echo "🚀 开始部署Telegram多会话客户端系统到服务器..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印状态
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查并安装依赖
install_dependencies() {
    print_status "检查系统依赖..."
    
    # 更新包管理器
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip nodejs npm nginx git curl
    elif command -v yum &> /dev/null; then
        sudo yum update -y
        sudo yum install -y python3 python3-pip nodejs npm nginx git curl
    else
        print_error "不支持的包管理器，请手动安装依赖"
        exit 1
    fi
    
    print_success "系统依赖安装完成"
}

# 配置防火墙
configure_firewall() {
    print_status "配置防火墙规则..."
    
    # 开放必要端口
    if command -v ufw &> /dev/null; then
        sudo ufw allow 80
        sudo ufw allow 443
        sudo ufw allow 8000
        sudo ufw allow 3000
        print_success "UFW防火墙规则已配置"
    elif command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --permanent --add-port=8000/tcp
        sudo firewall-cmd --permanent --add-port=3000/tcp
        sudo firewall-cmd --reload
        print_success "Firewalld防火墙规则已配置"
    else
        print_warning "未检测到防火墙，请手动开放端口: 80, 443, 8000, 3000"
    fi
}

# 安装Python依赖
setup_python_backend() {
    print_status "设置Python后端..."
    
    cd /workspace
    
    # 安装Python依赖
    pip3 install --break-system-packages fastapi uvicorn telethon requests
    
    print_success "Python后端设置完成"
}

# 配置Telegram-TT
setup_telegram_tt() {
    print_status "配置Telegram-TT客户端..."
    
    cd /workspace/telegram-tt
    
    # 确保.env文件存在
    if [ ! -f .env ]; then
        cat > .env << EOF
NODE_ENV=production
TELEGRAM_API_ID=27941788
TELEGRAM_API_HASH=0cd0979dc85b2433a7648342e7fce258
BASE_URL=http://$(hostname -I | awk '{print $1}'):3000/
EOF
    fi
    
    # 构建生产版本
    npm run build
    
    print_success "Telegram-TT配置完成"
}

# 配置Nginx反向代理
configure_nginx() {
    print_status "配置Nginx反向代理..."
    
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    # 创建Nginx配置
    sudo tee /etc/nginx/sites-available/telegram-client << EOF
server {
    listen 80;
    server_name $SERVER_IP;
    
    # 启动器页面
    location / {
        root /workspace;
        index telegram-tt-launcher.html;
        try_files \$uri \$uri/ =404;
    }
    
    # 静态文件
    location /static/ {
        root /workspace;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Telegram-TT客户端
    location /app/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Web客户端
    location /webclient/ {
        alias /workspace/;
        try_files \$uri telegram_web_client.html;
    }
}
EOF
    
    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/telegram-client /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    
    print_success "Nginx配置完成"
}

# 创建系统服务
create_systemd_services() {
    print_status "创建系统服务..."
    
    # FastAPI后端服务
    sudo tee /etc/systemd/system/telegram-api.service << EOF
[Unit]
Description=Telegram API Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/workspace
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Telegram-TT服务
    sudo tee /etc/systemd/system/telegram-tt.service << EOF
[Unit]
Description=Telegram-TT Client
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/workspace/telegram-tt
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载systemd并启动服务
    sudo systemctl daemon-reload
    sudo systemctl enable telegram-api telegram-tt nginx
    sudo systemctl start telegram-api telegram-tt nginx
    
    print_success "系统服务创建并启动完成"
}

# 更新启动器配置
update_launcher_config() {
    print_status "更新启动器配置..."
    
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    # 创建适用于服务器的启动器
    sed "s/localhost:8000/$SERVER_IP/g; s/localhost:3000/$SERVER_IP\/app/g" \
        /workspace/telegram-tt-launcher.html > /workspace/telegram-tt-launcher-server.html
    
    # 创建适用于服务器的Web客户端
    sed "s/localhost:8000/$SERVER_IP\/api/g" \
        /workspace/telegram_web_client.html > /workspace/telegram_web_client_server.html
    
    print_success "启动器配置更新完成"
}

# 创建快速访问页面
create_index_page() {
    print_status "创建主页..."
    
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    cat > /workspace/index.html << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram多会话客户端系统</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 600px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .btn {
            display: inline-block;
            padding: 15px 30px;
            margin: 10px;
            background: #2196F3;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #1976D2;
            transform: translateY(-2px);
        }
        .info {
            background: #f0f8ff;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }
        .mobile-note {
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Telegram多会话客户端系统</h1>
        
        <div class="info">
            <h3>📱 移动设备访问</h3>
            <p>在手机浏览器中扫描二维码或直接访问：</p>
            <p><strong>http://$SERVER_IP</strong></p>
        </div>
        
        <div class="mobile-note">
            <h3>📋 使用说明</h3>
            <p>1. 点击"启动器"管理多个会话</p>
            <p>2. 点击"Web客户端"使用轻量版</p>
            <p>3. 每个子域名对应独立的Telegram会话</p>
        </div>
        
        <div>
            <a href="telegram-tt-launcher-server.html" class="btn">🚀 多会话启动器</a>
            <a href="telegram_web_client_server.html" class="btn">🌐 Web客户端</a>
            <a href="/app/" class="btn">📱 Telegram-TT</a>
        </div>
        
        <div style="margin-top: 30px; font-size: 14px; color: #666;">
            <p>服务器IP: $SERVER_IP</p>
            <p>API后端: <a href="http://$SERVER_IP/api/debug/session" target="_blank">$SERVER_IP/api</a></p>
            <p>系统状态: <span style="color: green;">运行中</span></p>
        </div>
    </div>
</body>
</html>
EOF

    print_success "主页创建完成"
}

# 生成访问信息
generate_access_info() {
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "=========================================="
    echo "🎉 部署完成！"
    echo "=========================================="
    echo ""
    echo "📱 手机访问地址："
    echo "   主页: http://$SERVER_IP"
    echo "   启动器: http://$SERVER_IP/telegram-tt-launcher-server.html"
    echo "   Web客户端: http://$SERVER_IP/telegram_web_client_server.html"
    echo ""
    echo "🖥️ 桌面访问地址："
    echo "   Telegram-TT: http://$SERVER_IP/app/"
    echo "   API后端: http://$SERVER_IP/api/"
    echo ""
    echo "🔧 服务状态检查："
    echo "   sudo systemctl status telegram-api"
    echo "   sudo systemctl status telegram-tt"
    echo "   sudo systemctl status nginx"
    echo ""
    echo "📋 使用说明："
    echo "1. 在手机浏览器中访问主页"
    echo "2. 选择启动器或Web客户端"
    echo "3. 输入子域名（如：user1）"
    echo "4. 完成快速登录"
    echo "5. 启动客户端开始使用"
    echo ""
    echo "🔐 重要提醒："
    echo "- 每个子域名对应独立会话"
    echo "- 支持同时登录多个账号"
    echo "- 不会出现掉号问题"
    echo "=========================================="
}

# 主执行流程
main() {
    print_status "开始服务器部署..."
    
    # 检查是否为root用户
    if [[ $EUID -eq 0 ]]; then
        print_error "请不要使用root用户运行此脚本"
        exit 1
    fi
    
    # 执行部署步骤
    install_dependencies
    configure_firewall
    setup_python_backend
    setup_telegram_tt
    configure_nginx
    create_systemd_services
    update_launcher_config
    create_index_page
    
    # 等待服务启动
    print_status "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if systemctl is-active --quiet telegram-api; then
        print_success "API后端服务运行正常"
    else
        print_error "API后端服务启动失败"
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "Nginx服务运行正常"
    else
        print_error "Nginx服务启动失败"
    fi
    
    # 生成访问信息
    generate_access_info
}

# 如果直接运行脚本则执行main函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi