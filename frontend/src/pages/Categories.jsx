import { useEffect, useState, useCallback } from 'react'
import {
  Table, Button, Modal, Form, Input, Space, Popconfirm, Input as AntInput,
} from 'antd'
import { PlusOutlined, ReloadOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import {
  listCategories, createCategory, updateCategory, deleteCategory,
} from '../api/category'

export default function Categories() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [keyword, setKeyword] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = keyword ? { name: keyword } : {}
      const list = await listCategories(params)
      setData(list || [])
    } finally {
      setLoading(false)
    }
  }, [keyword])

  useEffect(() => { fetchData() }, [fetchData])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
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
      await updateCategory(editing.id, values)
    } else {
      await createCategory(values)
    }
    setModalOpen(false)
    fetchData()
  }

  const onDelete = async (id) => {
    await deleteCategory(id)
    fetchData()
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '分类名称', dataIndex: 'name' },
    { title: '编码', dataIndex: 'code', width: 120 },
    { title: '描述', dataIndex: 'description', ellipsis: true },
    {
      title: '创建时间', dataIndex: 'created_at', width: 180,
      render: (v) => (v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '-'),
    },
    {
      title: '操作', width: 160, render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确认删除该分类？" onConfirm={() => onDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      <h2 style={{ marginTop: 0 }}>分类管理</h2>
      <div className="page-toolbar">
        <AntInput
          allowClear
          placeholder="按名称搜索"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          style={{ width: 200 }}
          onPressEnter={fetchData}
        />
        <Button type="primary" onClick={fetchData}>搜索</Button>
        <Button icon={<ReloadOutlined />} onClick={() => { setKeyword(''); fetchData() }}>重置</Button>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate} style={{ marginLeft: 'auto' }}>
          新增分类
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={data}
        pagination={{ pageSize: 10, showSizeChanger: true }}
      />

      <Modal
        title={editing ? '编辑分类' : '新增分类'}
        open={modalOpen}
        onOk={onSubmit}
        onCancel={() => setModalOpen(false)}
        okText="保存"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="分类名称" rules={[{ required: true, message: '请输入分类名称' }]}>
            <Input placeholder="如：计算机科学" maxLength={64} />
          </Form.Item>
          <Form.Item name="code" label="分类编码">
            <Input placeholder="如：CS" maxLength={32} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} maxLength={255} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
