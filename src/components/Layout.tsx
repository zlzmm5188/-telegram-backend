import React from 'react'
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { UserOutlined, DashboardOutlined, TeamOutlined, LogoutOutlined } from '@ant-design/icons'
import { useAuthStore } from '../stores/auth'

const { Header, Content, Sider } = AntLayout

function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
      onClick: () => navigate('/dashboard'),
    },
    ...(user?.role === 'admin' ? [{
      key: '/agent',
      icon: <TeamOutlined />,
      label: '代理中心',
      onClick: () => navigate('/agent'),
    }] : []),
  ]

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

  return (
    <AntLayout className="dashboard-layout">
      <Sider width={200} style={{ background: '#fff' }}>
        <div style={{ padding: '16px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
          <h2 style={{ margin: 0, color: '#1890ff' }}>📱 Telegram 管理</h2>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ height: '100%', borderRight: 0 }}
        />
      </Sider>
      <AntLayout>
        <Header className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, color: '#333' }}>
            {location.pathname === '/dashboard' ? '仪表盘' : 
             location.pathname === '/agent' ? '代理中心' : '管理系统'}
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span>欢迎，{user?.username}</span>
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
            </Dropdown>
          </div>
        </Header>
        <Content style={{ margin: '24px 24px 0', overflow: 'initial' }}>
          <div className="dashboard-content">
            <Outlet />
          </div>
        </Content>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout