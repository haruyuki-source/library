# 图书馆管理系统

基于 **Vue 3 + Flask** 前后端分离架构的图书馆管理系统，实现图书管理、读者管理、分类管理、借阅管理等核心功能，支持桌面端与移动端自适应显示。

---

## 一、技术栈

### 前端

| 技术 | 版本 | 说明 |
|---|---|---|
| Vue | ^3.4.21 | 渐进式前端框架，Composition API |
| Vite | ^5.2.0 | 前端构建工具，极速 HMR |
| Element Plus | ^2.7.0 | Vue 3 组件库，管理后台 UI |
| Vue Router | ^4.3.0 | 路由管理 + 登录守卫 |
| Pinia | ^2.1.7 | 状态管理（登录态持久化） |
| Axios | ^1.6.8 | HTTP 请求库 |
| @element-plus/icons-vue | ^2.3.1 | Element Plus 图标 |

### 后端

| 技术 | 说明 |
|---|---|
| Flask | 轻量级 Python Web 框架 |
| Flask-SQLAlchemy | ORM 框架，数据库操作 |
| Flask-Migrate | 数据库迁移（Alembic） |
| Flask-JWT-Extended | JWT 无状态鉴权 |
| Flask-CORS | 跨域资源共享 |
| Marshmallow | 请求参数序列化与校验 |
| PyMySQL | MySQL 驱动（可选，默认 SQLite） |

### 数据库

- **默认**：SQLite（嵌入式，零配置，文件存储于 `backend/library.db`）
- **可选**：MySQL（通过环境变量 `SQLALCHEMY_DATABASE_URI` 切换）

---

## 二、项目结构

```
.
├── backend/                    # 后端 Flask 项目
│   ├── app/
│   │   ├── __init__.py         # 应用工厂：注册蓝图、初始化扩展、种子数据
│   │   ├── config.py           # 配置（密钥、数据库、分页等）
│   │   ├── extensions.py       # 扩展实例（db/jwt/cors/migrate）
│   │   ├── models.py           # 数据模型 + Marshmallow Schemas
│   │   └── api/                # 业务接口蓝图
│   │       ├── auth_api.py     # 登录 / 当前用户
│   │       ├── book_api.py     # 图书 CRUD + 搜索
│   │       ├── reader_api.py   # 读者 CRUD + 搜索
│   │       ├── category_api.py # 分类 CRUD
│   │       └── borrow_api.py   # 借书 / 还书 / 续借
│   ├── library.db              # SQLite 数据库文件（自动生成）
│   ├── requirements.txt        # Python 依赖
│   └── run.py                  # 启动入口（端口 5000）
│
├── frontend/                   # 前端 Vue 3 项目
│   ├── src/
│   │   ├── main.js             # 应用入口
│   │   ├── App.vue             # 根组件
│   │   ├── api/                # 接口封装
│   │   │   ├── request.js      # Axios 实例 + 拦截器
│   │   │   ├── auth.js
│   │   │   ├── book.js
│   │   │   ├── reader.js
│   │   │   ├── category.js
│   │   │   └── borrow.js
│   │   ├── router/index.js     # 路由表 + 登录守卫
│   │   ├── store/auth.js       # Pinia 鉴权状态
│   │   ├── layouts/
│   │   │   └── MainLayout.vue  # 主布局（响应式侧边栏 + 顶栏）
│   │   ├── views/              # 页面
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Book.vue
│   │   │   ├── Reader.vue
│   │   │   ├── Category.vue
│   │   │   ├── Borrow.vue
│   │   │   └── NotFound.vue
│   │   └── styles/main.css     # 全局样式 + 移动端适配
│   ├── index.html
│   ├── vite.config.js          # Vite 配置（/api 代理到 5000）
│   └── package.json
│
└── README.md
```

---

## 三、功能模块

| 模块 | 功能 |
|---|---|
| 登录鉴权 | 用户名密码登录、JWT 签发、401 自动跳转登录页 |
| 首页概览 | 图书/读者/借阅/分类统计卡片 |
| 图书管理 | 图书列表、关键词搜索、分页、新增/编辑/删除 |
| 读者管理 | 读者列表、搜索、分页、新增/编辑/删除 |
| 分类管理 | 分类 CRUD |
| 借阅管理 | 借书、还书（自动计算逾期罚金）、续借、删除 |

---

## 四、环境要求

- **Python** ≥ 3.8
- **Node.js** ≥ 16
- **npm** ≥ 8

---

## 五、快速开始

### 1. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动（默认端口 5000，debug 模式）
python run.py
```

后端启动后会自动：
- 创建数据库表
- 插入默认管理员、分类、读者、图书示例数据

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认端口 5173）
npm run dev
```

### 3. 访问

- 前端：http://localhost:5173
- 后端：http://localhost:5000
- 后端健康检查：http://localhost:5000/api/health

### 4. 默认账号

| 用户名 | 密码 | 角色 |
|---|---|---|
| admin | admin123 | 超级管理员 |

---

## 六、API 接口概览

所有接口前缀：`/api`，响应统一格式：

```json
{ "code": 0, "msg": "ok", "data": { ... } }
```

### 鉴权

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/auth/login` | 登录，返回 JWT |
| GET | `/api/auth/profile` | 当前用户信息（需 Bearer Token） |

### 图书

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/books` | 列表（支持 `keyword`、`category_id`、`page`、`page_size`） |
| GET | `/api/books/:id` | 详情 |
| POST | `/api/books` | 新增 |
| PUT | `/api/books/:id` | 更新 |
| DELETE | `/api/books/:id` | 删除 |

### 读者

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/readers` | 列表（支持 `keyword`、`page`、`page_size`） |
| POST | `/api/readers` | 新增 |
| PUT | `/api/readers/:id` | 更新 |
| DELETE | `/api/readers/:id` | 删除 |

### 分类

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/categories` | 列表 |
| POST | `/api/categories` | 新增 |
| PUT | `/api/categories/:id` | 更新 |
| DELETE | `/api/categories/:id` | 删除 |

### 借阅

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/borrow` | 记录列表（支持 `status` 过滤） |
| POST | `/api/borrow` | 借书（需登录） |
| PUT | `/api/borrow/:id/return` | 还书（需登录，自动计罚金） |
| PUT | `/api/borrow/:id/renew` | 续借（需登录） |
| DELETE | `/api/borrow/:id` | 删除记录（需登录） |

---

## 七、数据库说明

- 默认使用 SQLite，数据库文件为 `backend/library.db`，首次启动自动创建。
- 切换到 MySQL：设置环境变量
  ```bash
  export SQLALCHEMY_DATABASE_URI="mysql+pymysql://user:password@localhost:3306/library"
  ```

### 数据模型

| 表 | 说明 |
|---|---|
| admins | 管理员（登录用户） |
| categories | 图书分类 |
| books | 图书 |
| readers | 读者 |
| borrow_records | 借阅记录 |

---

## 八、移动端适配

- 桌面端：常驻左侧导航栏（220px）+ 顶部栏
- 移动端（≤768px）：左侧栏变为抽屉式，顶部栏左侧显示汉堡按钮
- 表格支持横向滚动，弹窗自动限宽，分页器窄屏紧凑显示

---

## 九、生产构建

```bash
cd frontend
npm run build      # 产物输出到 frontend/dist
npm run preview    # 本地预览构建产物
```

可将 `dist/` 目录部署到 Nginx 等静态服务器，并配置 `/api` 反向代理到后端 Flask 服务。
