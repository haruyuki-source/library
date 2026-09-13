# 图书馆管理系统

基于 **Vue 3 + Flask** 前后端分离架构的图书馆管理系统，分为**管理员端**与**学生端**两个入口（JWT 角色隔离），实现图书管理、读者管理、分类管理、借阅管理、**线上预约索书**（学生预约 → 到馆管理员确认后转借阅并扣减库存）等核心功能，支持桌面端与移动端自适应显示。

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
│   │       ├── decorators.py   # JWT 角色装饰器：admin_required / reader_required
│   │       ├── auth_api.py     # 管理员登录 / 当前用户
│   │       ├── book_api.py     # 图书 CRUD + 搜索
│   │       ├── reader_api.py   # 读者 CRUD + 搜索
│   │       ├── category_api.py # 分类 CRUD
│   │       ├── borrow_api.py   # 借书 / 还书 / 续借
│   │       ├── reservation_api.py # 管理员预约管理：确认借书(转借阅+扣库存)/取消
│   │       └── student_api.py  # 学生端：登录/资料/改密/我的借阅/预约/取消预约
│   ├── library.db              # SQLite 数据库文件（自动生成）
│   ├── requirements.txt        # Python 依赖
│   └── run.py                  # 启动入口（端口 5000）
│
├── frontend/                   # 前端 Vue 3 项目
│   ├── src/
│   │   ├── main.js             # 应用入口
│   │   ├── App.vue             # 根组件
│   │   ├── api/                # 接口封装
│   │   │   ├── request.js      # Axios 双实例(admin/student) + 拦截器
│   │   │   ├── auth.js
│   │   │   ├── book.js
│   │   │   ├── reader.js
│   │   │   ├── category.js
│   │   │   ├── borrow.js
│   │   │   ├── reservation.js  # 管理员预约管理接口
│   │   │   └── student.js      # 学生端接口
│   │   ├── router/index.js     # 路由表 + 登录守卫(双端隔离)
│   │   ├── store/
│   │   │   ├── auth.js         # Pinia 管理员鉴权状态
│   │   │   └── student.js      # Pinia 学生鉴权状态
│   │   ├── layouts/
│   │   │   ├── MainLayout.vue  # 管理员端布局(响应式侧边栏 + 顶栏)
│   │   │   └── StudentLayout.vue # 学生端布局
│   │   ├── views/              # 页面
│   │   │   ├── Login.vue       # 登录页(管理员/学生角色切换,双端复用)
│   │   │   ├── Dashboard.vue   # 管理员首页概览
│   │   │   ├── Book.vue
│   │   │   ├── Reader.vue
│   │   │   ├── Category.vue
│   │   │   ├── Borrow.vue
│   │   │   ├── Reservation.vue # 管理员预约管理
│   │   │   ├── NotFound.vue
│   │   │   └── student/        # 学生端页面
│   │   │       ├── StudentBooks.vue        # 图书检索 / 预约
│   │   │       ├── StudentReservations.vue # 我的预约
│   │   │       ├── StudentBorrows.vue      # 我的借阅
│   │   │       ├── StudentProfile.vue      # 个人信息
│   │   │       └── StudentPassword.vue     # 修改密码
│   │   └── styles/main.css     # 全局样式 + 移动端适配
│   ├── index.html
│   ├── vite.config.js          # Vite 配置（/api 代理到 5000）
│   └── package.json
│
└── README.md
```

---

## 三、功能模块

### 管理员端（`/login`）

| 模块 | 功能 |
|---|---|
| 登录鉴权 | 用户名密码登录、JWT 签发、401 自动跳转登录页 |
| 首页概览 | 图书/读者/借阅中/分类/预约中统计卡片（点击跳转对应管理页） |
| 图书管理 | 图书列表、关键词搜索、分页、新增/编辑/删除 |
| 读者管理 | 读者列表、搜索、分页、新增/编辑/删除、设置可借上限 |
| 分类管理 | 分类 CRUD |
| 借阅管理 | 借书、还书（自动计算逾期罚金）、续借、删除 |
| 预约管理 | 预约列表（状态/读者/图书筛选）、扫码或输入预约号快速办理、确认借书、取消预约 |

### 学生端（`/student/login`）

| 模块 | 功能 |
|---|---|
| 登录鉴权 | 借书证号 + 密码登录、忘记密码（预留手机号）、JWT 角色隔离 |
| 图书检索 | 图书搜索、查看可借库存、在线预约 |
| 我的预约 | 查看预约记录与保留期限、取消预约 |
| 我的借阅 | 查看在借/历史借阅、应还日期 |
| 个人信息 | 查看本人资料（点击顶部用户名进入） |
| 修改密码 | 自助修改登录密码 |

### 预约索书业务流程

```
学生在线预约(状态:预约中,库存不扣减,保留期 7 天)
        │
        ├── 学生在保留期内可主动取消
        │
        ▼
学生到馆 → 管理员在「预约管理」确认借书
        │  (同一事务内:校验库存 → 生成借阅记录(借期30天) → 可借库存 -1 → 预约转已办理)
        ▼
   状态:借阅中
```

> 库存扣减唯一入口为管理员的「确认借书」动作；学生端任何操作都不会直接扣减库存。

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

- 管理员端：http://localhost:5173/login
- 学生端：http://localhost:5173/student/login
- 后端：http://localhost:5000
- 后端健康检查：http://localhost:5000/api/health

### 4. 默认账号

管理员：

| 用户名 | 密码 | 角色 |
|---|---|---|
| admin | admin123 | 超级管理员 |

学生（密码与借书证号相同）：

| 借书证号（账号/密码） | 姓名 |
|---|---|
| R2024001 | 张三 |
| R2024002 | 李四 |
| R2024003 | 王五 |

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

### 学生端（前缀 `/api/student`，读者 Token）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/login` | 借书证号 + 密码登录 |
| POST | `/forgot-password` | 忘记密码（校验预留手机号） |
| GET | `/profile` | 当前学生信息 |
| PUT | `/password` | 修改密码 |
| GET | `/borrows` | 我的借阅记录 |
| GET | `/borrows/active` | 当前在借 |
| POST | `/reservations` | 预约图书（**不扣库存**，保留期 7 天） |
| GET | `/reservations` | 我的预约（支持 `status` 过滤） |
| POST | `/reservations/:id/cancel` | 取消本人预约（仅预约中可取消） |

> 学生端图书检索/分类直接复用公共接口 `GET /api/books`、`GET /api/categories`（无需管理员权限）。

### 预约管理（前缀 `/api/reservations`，管理员 Token）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `` | 预约列表（`status`/`reader_id`/`book_id` 过滤 + 分页） |
| GET | `/:id` | 预约详情 |
| PUT | `/:id/fulfill` | **确认借书**：转借阅 + 扣减 1 本库存（同一事务） |
| PUT | `/:id/cancel` | 管理员取消预约 |

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
| reservations | 预约记录（reserved 预约中 / fulfilled 已办理 / cancelled 已取消） |

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
