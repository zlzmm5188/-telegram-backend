import React, { useState, useEffect } from 'react'
import { Table, Button, Input, Form, message, Modal, Space, Popconfirm } from 'antd'
import { SearchOutlined, ReloadOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { agentAPI } from '../services/api'
import type { User, AgentSearchParams, CreateAgentRequest } from '../types'

function Agent() {
  const [data, setData] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [searchParams, setSearchParams] = useState<AgentSearchParams>({
    page: 1,
    pageSize: 20,
  })
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [createForm] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
      const response = await agentAPI.getAgents(searchParams)
      if (response.success) {
        setData(response.data || [])
        setTotal(response.total || 0)
      }
    } catch (error: any) {
      message.error('获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [searchParams])

  const handleSearch = (values: any) => {
    setSearchParams({
      ...searchParams,
      page: 1,
      username: values.username || undefined,
    })
  }

  const handleReset = () => {
    setSearchParams({ page: 1, pageSize: 20 })
  }

  const handleCreate = async () => {
    try {
      const values = await createForm.validateFields()
      await agentAPI.createAgent(values as CreateAgentRequest)
      message.success('代理创建成功')
      setCreateModalVisible(false)
      createForm.resetFields()
      fetchData()
    } catch (error: any) {
      message.error(error.response?.data?.message || '创建失败')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await agentAPI.deleteAgent(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const formatTime = (timestamp: number) => {
    return dayjs(timestamp * 1000).format('YYYY-MM-DD HH:mm:ss')
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      width: 150,
    },
    {
      title: '邀请码',
      dataIndex: 'invite_code',
      width: 120,
    },
    {
      title: '角色',
      dataIndex: 'role',
      width: 100,
      render: (role: string) => role === 'admin' ? '管理员' : '代理',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (time: number) => formatTime(time),
    },
    {
      title: '操作',
      width: 120,
      render: (record: User) => (
        <Popconfirm
          title="确认删除"
          description="确定要删除这个代理吗？"
          onConfirm={() => handleDelete(record.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
          >
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="username">
            <Input placeholder="用户名" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                搜索
              </Button>
              <Button onClick={handleReset} icon={<ReloadOutlined />}>
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
        
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setCreateModalVisible(true)}
        >
          创建代理
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          current: searchParams.page,
          pageSize: searchParams.pageSize,
          total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setSearchParams({ ...searchParams, page, pageSize: pageSize || 20 })
          },
        }}
      />

      <Modal
        title="创建代理"
        open={createModalVisible}
        onOk={handleCreate}
        onCancel={() => {
          setCreateModalVisible(false)
          createForm.resetFields()
        }}
        okText="创建"
        cancelText="取消"
      >
        <Form form={createForm} layout="vertical">
          <Form.Item
            name="username"
            label="用户名"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
            ]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>
          <Form.Item
            name="password"
            label="密码"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Agent