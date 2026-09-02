import { useEffect, useState, useCallback } from 'react'
import {
  Table, Button, Modal, Form, InputNumber, Select, Space, Tag, Input, message,
} from 'antd'
import { PlusOutlined, ReloadOutlined, ExportOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import {
  listBorrowRecords, borrowBook, returnBook, renewBook, listOverdue,
} from '../api/borrow'
import { listReaders } from '../api/reader'
import { listBooks } from '../api/book'

const STATUS_OPTIONS = [
  { label: '全部', value: '' },
  { label: '借阅中', value: 'borrowed' },
  { label: '已归还', value: 'returned' },
  { label: '逾期', value: 'overdue' },
]

const STATUS_TAG = {
  borrowed: { text: '借阅中', color: 'blue' },
  returned: { text: '已归还', color: 'default' },
  overdue: { text: '逾期', color: 'red' },
  lost: { text: '丢失', color: 'orange' },
}

export default function BorrowRecords() {
  const [data, setData] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState({ page: 1, per_page: 10, reader_id: undefined, status: '' })
  const [modalOpen, setModalOpen] = useState(false)
  const [overdueOpen, setOverdueOpen] = useState(false)
  const [overdueList, setOverdueList] = useState([])
  const [overdueLoading, setOverdueLoading] = useState(false)
  const [readers, setReaders] = useState([])
  const [books, setBooks] = useState([])
  const [form] = Form.useForm()

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page: query.page, per_page: query.per_page }
      if (query.reader_id) params.reader_id = query.reader_id
      if (query.status) params.status = query.status
      const res = await listBorrowRecords(params)
      setData(res.items || [])
      setTotal(res.total || 0)
    } finally {
      setLoading(false)
    }
  }, [query])

  useEffect(() => { fetchData() }, [fetchData])

  // 打开借书弹窗时，懒加载读者/图书下拉数据
  const openBorrow = async () => {
    form.resetFields()
    form.setFieldsValue({ due_days: 30 })
    setModalOpen(true)
    if (!readers.length) {
      const r = await listReaders({ page: 1, per_page: 100 })
      setReaders(r.items || [])
    }
    if (!books.length) {
      const b = await listBooks({ page: 1, per_page: 100 })
      setBooks(b.items || [])
    }
  }

  const onBorrow = async () => {
    const values = await form.validateFields()
    await borrowBook(values)
    message.success('借阅成功')
    setModalOpen(false)
    fetchData()
  }

  const onReturn = async (record) => {
    await returnBook(record.id)
    fetchData()
  }

  const onRenew = async (record) => {
    await renewBook(record.id, 30)
    fetchData()
  }

  const openOverdue = async () => {
    setOverdueOpen(true)
    setOverdueLoading(true)
    try {
      const list = await listOverdue()
      setOverdueList(list || [])
    } finally {
      setOverdueLoading(false)
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: '读者', width: 140,
      render: (_, r) => r.reader ? `${r.reader.name} (${r.reader.card_no})` : r.reader_id,
    },
    {
      title: '图书', ellipsis: true,
      render: (_, r) => r.book ? `${r.book.title} - ${r.book.author || '-'}` : r.book_id,
    },
    {
      title: '借阅日期', dataIndex: 'borrow_date', width: 120,
      render: (v) => v ? dayjs(v).format('YYYY-MM-DD') : '-',
    },
    {
      title: '应还日期', dataIndex: 'due_date', width: 120,
      render: (v) => v ? dayjs(v).format('YYYY-MM-DD') : '-',
    },
    {
      title: '归还日期', dataIndex: 'return_date', width: 120,
      render: (v) => v ? dayjs(v).format('YYYY-MM-DD') : '-',
    },
    {
      title: '状态', width: 100,
      render: (_, r) => {
        const t = STATUS_TAG[r.status] || { text: r.status, color: 'default' }
        return <Tag color={t.color}>{t.text}</Tag>
      },
    },
    { title: '续借', dataIndex: 'renew_count', width: 70 },
    {
      title: '罚金', width: 100,
      render: (_, r) => (r.fine_amount > 0 ? (
        <span style={{ color: r.fine_paid ? '#52c41a' : '#ff4d4f' }}>
          ¥{r.fine_amount}{r.fine_paid ? '(已付)' : '(未付)'}
        </span>
      ) : '-'),
    },
    {
      title: '操作', width: 160, render: (_, record) => (
        <Space>
          {record.status === 'borrowed' && (
            <>
              <Button size="small" onClick={() => onRenew(record)}>续借</Button>
              <Button size="small" type="primary" onClick={() => onReturn(record)}>归还</Button>
            </>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      <h2 style={{ marginTop: 0 }}>借阅管理</h2>

      <div className="page-toolbar">
        <Select
          allowClear
          showSearch
          placeholder="选择读者"
          value={query.reader_id}
          onChange={(v) => setQuery((q) => ({ ...q, reader_id: v, page: 1 }))}
          style={{ width: 220 }}
          optionFilterProp="label"
          options={readers.length ? readers.map((r) => ({ label: `${r.name} (${r.card_no})`, value: r.id })) : []}
          onFocus={async () => {
            if (!readers.length) {
              const r = await listReaders({ page: 1, per_page: 100 })
              setReaders(r.items || [])
            }
          }}
        />
        <Select
          placeholder="状态"
          value={query.status}
          onChange={(v) => setQuery((q) => ({ ...q, status: v || '', page: 1 }))}
          style={{ width: 120 }}
          options={STATUS_OPTIONS}
        />
        <Button type="primary" onClick={() => setQuery((q) => ({ ...q, page: 1 }))}>搜索</Button>
        <Button icon={<ReloadOutlined />} onClick={() => setQuery({ page: 1, per_page: 10, reader_id: undefined, status: '' })}>重置</Button>
        <Button icon={<ExportOutlined />} onClick={openOverdue}>逾期列表</Button>
        <Button type="primary" icon={<PlusOutlined />} onClick={openBorrow} style={{ marginLeft: 'auto' }}>
          借书
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={data}
        scroll={{ x: 1200 }}
        pagination={{
          current: query.page, pageSize: query.per_page, total,
          showSizeChanger: true, showTotal: (t) => `共 ${t} 条`,
          onChange: (page, per_page) => setQuery((q) => ({ ...q, page, per_page })),
        }}
      />

      <Modal
        title="新增借阅"
        open={modalOpen}
        onOk={onBorrow}
        onCancel={() => setModalOpen(false)}
        okText="确认借阅"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="reader_id" label="读者" rules={[{ required: true, message: '请选择读者' }]}>
            <Select
              showSearch
              placeholder="选择读者"
              optionFilterProp="label"
              options={readers.map((r) => ({ label: `${r.name} (${r.card_no})`, value: r.id }))}
            />
          </Form.Item>
          <Form.Item name="book_id" label="图书" rules={[{ required: true, message: '请选择图书' }]}>
            <Select
              showSearch
              placeholder="选择图书"
              optionFilterProp="label"
              options={books.map((b) => ({ label: `${b.title} (剩${b.available_quantity})`, value: b.id, disabled: b.available_quantity <= 0 }))}
            />
          </Form.Item>
          <Form.Item name="due_days" label="借阅天数" rules={[{ required: true }]}>
            <InputNumber min={1} max={180} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="remark" label="备注">
            <Input.TextArea rows={2} maxLength={500} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`逾期未还列表（${overdueList.length} 条）`}
        open={overdueOpen}
        onCancel={() => setOverdueOpen(false)}
        footer={null}
        width={900}
      >
        <Table
          rowKey="id"
          loading={overdueLoading}
          size="small"
          dataSource={overdueList}
          pagination={{ pageSize: 10 }}
          columns={[
            { title: '读者', width: 120, render: (_, r) => r.reader?.name || r.reader_id },
            { title: '图书', ellipsis: true, render: (_, r) => r.book?.title || r.book_id },
            { title: '应还日期', dataIndex: 'due_date', width: 120, render: (v) => v ? dayjs(v).format('YYYY-MM-DD') : '-' },
            { title: '应缴罚金', dataIndex: 'current_fine', width: 100, render: (v) => `¥${v || 0}` },
          ]}
        />
      </Modal>
    </div>
  )
}
