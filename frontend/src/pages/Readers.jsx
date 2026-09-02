import { useEffect, useState, useCallback } from 'react'
import {
  Table, Button, Modal, Form, Input, InputNumber, Select, Space, Popconfirm, Tag,
} from 'antd'
import { PlusOutlined, ReloadOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { listReaders, createReader, updateReader, deleteReader } from '../api/reader'

const GENDER_OPTIONS = [
  { label: '男', value: 'male' },
  { label: '女', value: 'female' },
  { label: '其他', value: 'other' },
]
const STATUS_OPTIONS = [
  { label: '正常', value: 'active' },
  { label: '禁用', value: 'disabled' },
]

export default function Readers() {
  const [data, setData] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState({ page: 1, per_page: 10, keyword: '', status: '', department: '' })
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page: query.page, per_page: query.per_page }
      if (query.keyword) params.keyword = query.keyword
      if (query.status) params.status = query.status
      if (query.department) params.department = query.department
      const res = await listReaders(params)
      setData(res.items || [])
      setTotal(res.total || 0)
    } finally {
      setLoading(false)
    }
  }, [query])

  useEffect(() => { fetchData() }, [fetchData])

  const onSearch = () => setQuery((q) => ({ ...q, page: 1 }))
  const onReset = () => setQuery({ page: 1, per_page: 10, keyword: '', status: '', department: '' })

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ gender: 'male', status: 'active', max_borrow: 5 })
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  const onSubmit = async () => {
    const values = await form.validateFields()
    if (editing) {
      await updateReader(editing.id, values)
    } else {
      await createReader(values)
    }
    setModalOpen(false)
    fetchData()
  }

  const onDelete = async (id) => {
    await deleteReader(id)
    fetchData()
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '借阅证号', dataIndex: 'card_no', width: 120 },
    { title: '姓名', dataIndex: 'name', width: 100 },
    {
      title: '性别', width: 70,
      render: (_, r) => ({ male: '男', female: '女', other: '其他' }[r.gender] || '-'),
    },
    { title: '电话', dataIndex: 'phone', width: 130 },
    { title: '邮箱', dataIndex: 'email', width: 180, ellipsis: true },
    { title: '部门', dataIndex: 'department', width: 140, ellipsis: true },
    {
      title: '状态', width: 80,
      render: (_, r) => <Tag color={r.status === 'active' ? 'green' : 'red'}>{r.status === 'active' ? '正常' : '禁用'}</Tag>,
    },
    {
      title: '在借/上限', width: 100,
      render: (_, r) => `${r.current_borrow_count ?? 0}/${r.max_borrow}`,
    },
    {
      title: '操作', width: 160, render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确认删除该读者？" onConfirm={() => onDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      <h2 style={{ marginTop: 0 }}>读者管理</h2>

      <div className="page-toolbar">
        <Input
          allowClear
          placeholder="姓名 / 证号 / 电话"
          value={query.keyword}
          onChange={(e) => setQuery((q) => ({ ...q, keyword: e.target.value }))}
          style={{ width: 200 }}
          onPressEnter={onSearch}
        />
        <Select
          allowClear
          placeholder="状态"
          value={query.status || undefined}
          onChange={(v) => setQuery((q) => ({ ...q, status: v || '' }))}
          style={{ width: 120 }}
          options={STATUS_OPTIONS}
        />
        <Input
          allowClear
          placeholder="部门"
          value={query.department}
          onChange={(e) => setQuery((q) => ({ ...q, department: e.target.value }))}
          style={{ width: 160 }}
          onPressEnter={onSearch}
        />
        <Button type="primary" onClick={onSearch}>搜索</Button>
        <Button icon={<ReloadOutlined />} onClick={onReset}>重置</Button>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate} style={{ marginLeft: 'auto' }}>
          新增读者
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={data}
        scroll={{ x: 1100 }}
        pagination={{
          current: query.page, pageSize: query.per_page, total,
          showSizeChanger: true, showTotal: (t) => `共 ${t} 条`,
          onChange: (page, per_page) => setQuery((q) => ({ ...q, page, per_page })),
        }}
      />

      <Modal
        title={editing ? '编辑读者' : '新增读者'}
        open={modalOpen}
        onOk={onSubmit}
        onCancel={() => setModalOpen(false)}
        okText="保存"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="card_no" label="借阅证号" rules={[{ required: true, message: '请输入借阅证号' }]}>
            <Input maxLength={32} />
          </Form.Item>
          <Form.Item name="name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input maxLength={64} />
          </Form.Item>
          <Form.Item name="gender" label="性别">
            <Select options={GENDER_OPTIONS} />
          </Form.Item>
          <Form.Item name="phone" label="电话">
            <Input maxLength={20} />
          </Form.Item>
          <Form.Item name="email" label="邮箱" rules={[{ type: 'email', message: '邮箱格式不正确' }]}>
            <Input maxLength={128} />
          </Form.Item>
          <Form.Item name="department" label="部门">
            <Input maxLength={128} />
          </Form.Item>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="status" label="状态" style={{ flex: 1 }}>
              <Select options={STATUS_OPTIONS} />
            </Form.Item>
            <Form.Item name="max_borrow" label="最大借阅数" style={{ flex: 1 }}>
              <InputNumber min={1} max={100} style={{ width: '100%' }} />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </div>
  )
}
