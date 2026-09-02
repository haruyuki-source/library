import { useEffect, useState, useCallback } from 'react'
import {
  Table, Button, Modal, Form, Input, InputNumber, Select, Space, Popconfirm, Tag,
} from 'antd'
import { PlusOutlined, ReloadOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { listBooks, createBook, updateBook, deleteBook } from '../api/book'
import { listCategories } from '../api/category'

export default function Books() {
  const [data, setData] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState({ page: 1, per_page: 10, keyword: '', category_id: undefined, author: '' })
  const [categories, setCategories] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const fetchCategories = useCallback(async () => {
    const list = await listCategories()
    setCategories(list || [])
  }, [])

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page: query.page, per_page: query.per_page }
      if (query.keyword) params.keyword = query.keyword
      if (query.category_id) params.category_id = query.category_id
      if (query.author) params.author = query.author
      const res = await listBooks(params)
      setData(res.items || [])
      setTotal(res.total || 0)
    } finally {
      setLoading(false)
    }
  }, [query])

  useEffect(() => { fetchCategories() }, [fetchCategories])
  useEffect(() => { fetchData() }, [fetchData])

  const onSearch = () => setQuery((q) => ({ ...q, page: 1 }))
  const onReset = () => setQuery({ page: 1, per_page: 10, keyword: '', category_id: undefined, author: '' })

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ total_quantity: 1, available_quantity: 1, price: 0 })
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue({
      ...record,
      category_id: record.category_id ?? undefined,
    })
    setModalOpen(true)
  }

  const onSubmit = async () => {
    const values = await form.validateFields()
    if (editing) {
      await updateBook(editing.id, values)
    } else {
      await createBook(values)
    }
    setModalOpen(false)
    fetchData()
  }

  const onDelete = async (id) => {
    await deleteBook(id)
    fetchData()
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '书名', dataIndex: 'title', ellipsis: true },
    { title: '作者', dataIndex: 'author', width: 120 },
    { title: 'ISBN', dataIndex: 'isbn', width: 140 },
    {
      title: '分类', width: 120,
      render: (_, r) => r.category?.name || '-',
    },
    {
      title: '库存', width: 110,
      render: (_, r) => (
        <span>
          <Tag color={r.available_quantity > 0 ? 'green' : 'red'}>
            {r.available_quantity}/{r.total_quantity}
          </Tag>
        </span>
      ),
    },
    { title: '位置', dataIndex: 'location', width: 100 },
    {
      title: '操作', width: 160, render: (_, record) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确认删除该图书？" onConfirm={() => onDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      <h2 style={{ marginTop: 0 }}>图书管理</h2>

      <div className="page-toolbar">
        <Input
          allowClear
          placeholder="书名 / ISBN"
          value={query.keyword}
          onChange={(e) => setQuery((q) => ({ ...q, keyword: e.target.value }))}
          style={{ width: 200 }}
          onPressEnter={onSearch}
        />
        <Select
          allowClear
          placeholder="选择分类"
          value={query.category_id}
          onChange={(v) => setQuery((q) => ({ ...q, category_id: v }))}
          style={{ width: 160 }}
          options={categories.map((c) => ({ label: c.name, value: c.id }))}
        />
        <Input
          allowClear
          placeholder="作者"
          value={query.author}
          onChange={(e) => setQuery((q) => ({ ...q, author: e.target.value }))}
          style={{ width: 160 }}
          onPressEnter={onSearch}
        />
        <Button type="primary" onClick={onSearch}>搜索</Button>
        <Button icon={<ReloadOutlined />} onClick={onReset}>重置</Button>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate} style={{ marginLeft: 'auto' }}>
          新增图书
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={data}
        pagination={{
          current: query.page, pageSize: query.per_page, total,
          showSizeChanger: true, showTotal: (t) => `共 ${t} 条`,
          onChange: (page, per_page) => setQuery((q) => ({ ...q, page, per_page })),
        }}
      />

      <Modal
        title={editing ? '编辑图书' : '新增图书'}
        open={modalOpen}
        onOk={onSubmit}
        onCancel={() => setModalOpen(false)}
        okText="保存"
        cancelText="取消"
        width={640}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="书名" rules={[{ required: true, message: '请输入书名' }]}>
            <Input maxLength={255} />
          </Form.Item>
          <Form.Item name="isbn" label="ISBN">
            <Input maxLength={32} />
          </Form.Item>
          <Form.Item name="author" label="作者">
            <Input maxLength={128} />
          </Form.Item>
          <Form.Item name="publisher" label="出版社">
            <Input maxLength={128} />
          </Form.Item>
          <Form.Item name="publish_year" label="出版年份">
            <InputNumber min={0} max={3000} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="category_id" label="分类">
            <Select
              allowClear
              placeholder="选择分类"
              options={categories.map((c) => ({ label: c.name, value: c.id }))}
            />
          </Form.Item>
          <Form.Item name="location" label="馆藏位置">
            <Input maxLength={64} />
          </Form.Item>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="total_quantity" label="总库存" style={{ flex: 1 }}>
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="available_quantity" label="可借数量" style={{ flex: 1 }}>
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="price" label="价格" style={{ flex: 1 }}>
              <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
            </Form.Item>
          </Space>
          <Form.Item name="description" label="简介">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="cover_url" label="封面 URL">
            <Input maxLength={500} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
