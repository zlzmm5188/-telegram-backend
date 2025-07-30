#!/bin/bash

# Telegram 管理系统部署脚本
echo "🚀 开始部署 Telegram 管理系统..."

# 安装 Python 依赖
echo "📦 安装后端依赖..."
cd backend
pip3 install -r requirements.txt
cd ..

# 安装 Node.js 依赖
echo "📦 安装前端依赖..."
npm install

# 构建前端
echo "🔨 构建前端..."
npm run build

# 创建启动脚本
echo "📝 创建启动脚本..."

# 后端启动脚本
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
python3 run.py
EOF

# 前端启动脚本
cat > start_frontend.sh << 'EOF'
#!/bin/bash
npm run dev
EOF

# 生产环境启动脚本
cat > start_production.sh << 'EOF'
#!/bin/bash
echo "启动后端服务..."
cd backend
nohup python3 run.py > backend.log 2>&1 &
echo "后端服务已启动，PID: $!"

echo "前端已构建完成，请配置 Nginx 指向 dist/ 目录"
EOF

# 设置执行权限
chmod +x start_backend.sh
chmod +x start_frontend.sh
chmod +x start_production.sh

echo "✅ 部署完成！"
echo ""
echo "🎯 启动方式："
echo "开发模式："
echo "  后端: ./start_backend.sh"
echo "  前端: ./start_frontend.sh"
echo ""
echo "生产模式："
echo "  ./start_production.sh"
echo ""
echo "📱 访问地址："
echo "  前端: http://your-server:3000"
echo "  后端: http://your-server:8000"
echo "  默认账户: admin / admin123"