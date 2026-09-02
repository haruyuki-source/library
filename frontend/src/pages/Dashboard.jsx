import { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic } from 'antd'
import {
  BookOutlined,
  TeamOutlined,
  AppstoreOutlined,
  SwapOutlined,
  ClockCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import { listBooks } from '../api/book'
import { listReaders } from '../api/reader'
import { listCategories } from '../api/category'
import { listBorrowRecords, listOverdue } from '../api/borrow'

export default function Dashboard() {
  const [stats, setStats] = useState({
    books: 0,
    readers: 0,
    categories: 0,
    records: 0,
    borrowed: 0,
    overdue: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 并发拉取各模块总数（per_page=1 减少数据量，仅取 total）
    Promise.all([
      listBooks({ page: 1, per_page: 1 }),
      listReaders({ page: 1, per_page: 1 }),
      listCategories(),
      listBorrowRecords({ page: 1, per_page: 1 }),
      listBorrowRecords({ page: 1, per_page: 1, status: 'borrowed' }),
      listOverdue(),
    ])
    .then(([books, readers, cats, records, borrowed, overdue]) => {
      setStats({
        books: books.total || 0,
        readers: readers.total || 0,
        categories: Array.isArray(cats) ? cats.length : 0,
        records: records.total || 0,
        borrowed: borrowed.total || 0,
        overdue: Array.isArray(overdue) ? overdue.length : 0,
      })
    })
    .finally(() => setLoading(false))
  }, [])

  const cards = [
    { title: '图书总数', value: stats.books, icon: <BookOutlined />, color: '#1677ff' },
    { title: '读者总数', value: stats.readers, icon: <TeamOutlined />, color: '#52c41a' },
    { title: '分类总数', value: stats.categories, icon: <AppstoreOutlined />, color: '#722ed1' },
    { title: '借阅记录', value: stats.records, icon: <SwapOutlined />, color: '#13c2c2' },
    { title: '当前在借', value: stats.borrowed, icon: <ClockCircleOutlined />, color: '#fa8c16' },
    { title: '逾期未还', value: stats.overdue, icon: <WarningOutlined />, color: '#ff4d4f' },
  ]

  return (
    <div className="page-container">
      <h2 style={{ marginTop: 0, marginBottom: 24 }}>仪表盘</h2>
      <Row gutter={[16, 16]} className="dashboard-row">
        {cards.map((c, idx) => (
          <Col xs={24} sm={12} md={8} lg={8} key={idx}>
            <Card className="stat-card" loading={loading}>
              <Statistic
                title={c.title}
                value={c.value}
                prefix={<span style={{ color: c.color }}>{c.icon}</span>}
              />
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  )
}
