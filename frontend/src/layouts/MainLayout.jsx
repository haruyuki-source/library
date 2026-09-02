import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Dropdown, Avatar, Space } from 'antd'
import {
  DashboardOutlined,
  BookOutlined,
  TeamOutlined,
  AppstoreOutlined,
  SwapOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons'
import { useAuth } from '../context/AuthContext'

const { Header, Sider, Content } = Layout

const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/books', icon: <BookOutlined />, label: '图书管理' },
  { key: '/readers', icon: <TeamOutlined />, label: '读者管理' },
  { key: '/categories', icon: <AppstoreOutlined />, label: '分类管理' },
  { key: '/borrow', icon: <SwapOutlined />, label: '借阅管理' },
]

export default function MainLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleMenuClick = ({ key }) => navigate(key)

  const userMenu = {
    items: [
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: '退出登录',
        onClick: () => {
          logout()
          navigate('/login', { replace: true })
        },
      },
    ],
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsible>
        <div
          style={{
            height: 56,
            margin: 8,
            color: '#fff',
            fontWeight: 600,
            fontSize: 16,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(255,255,255,0.08)',
            borderRadius: 6,
          }}
        >
          图书管理系统
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
          }}
        >
          <Dropdown menu={userMenu} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.real_name || user?.username || '管理员'}</span>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px 24px 0', minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
