# cnAgentOS - AI智能瞭望与智能问数系统

## 项目概述

cnAgentOS 是一个基于 Tornado 框架的 AI 智能瞭望与智能问数系统。系统采用经典的 MVC 三层架构，实现了用户认证功能，并计划扩展为包含数字员工、模型引擎、数据仓库、数智大屏等功能的综合性 AI 应用平台。

## 技术栈

### 后端技术
- **Python**: 3.12
- **Web框架**: Tornado 6.5.5
- **数据库**: SQLite3
- **密码加密**: bcrypt

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 样式设计
- **JavaScript**: 交互逻辑

### 前端组件库（本地化）
| 组件名称 | 版本 | 路径 | 说明 |
|---------|------|------|------|
| Bootstrap | 5.3.8 | `app/static/dist/bootstrap-5.3.8-dist/` | ✅ **已解压** - CSS 框架，响应式布局和 UI 组件 |
| Font Awesome | 5.15.4 | `app/static/dist/fontawesome-free-5.15.4-web/` | ✅ **已解压** - 矢量图标库 |
| Layui | 2.13.6 | `app/static/dist/layui/layui-v2.13.6/layui/` | ✅ **已解压** - 轻量级前端 UI 框架 |

> **重要提示**: 所有前端组件必须本地化使用，禁止引用互联网资源。三大前端组件库均已就绪，可以开始使用。

### 架构模式
- **MVC**: Model-View-Controller 三层架构
- **B/S**: Browser/Server 浏览器/服务器模式

## 项目架构

### MVC 架构说明

```
┌─────────────────────────────────────────────────────────┐
│                      用户请求                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Controller (控制层)                         │
│  - 接收请求，处理业务逻辑                                 │
│  - 调用 Model 获取数据                                   │
│  - 渲染 View 返回响应                                    │
└─────────────────────┬───────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Model (模型层)   │    │  View (视图层)    │
│  - 数据访问       │    │  - 页面渲染       │
│  - 业务逻辑       │    │  - 模板引擎       │
│  - 数据验证       │    │  - 静态资源       │
└──────────────────┘    └──────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                  数据库 (SQLite3)                        │
└─────────────────────────────────────────────────────────┘
```

## 目录结构

```
cnAgentOS/
│
├── app.py                      # 主入口文件，Tornado 应用启动和路由配置
├── app.md                      # 项目目录结构说明文件
├── app1.md                     # 项目目录结构说明文件（同 app.md）
├── requirements.md             # 开发需求文档
├── test.py                     # 单元测试脚本
├── 提示词.txt                   # 开发提示信息
│
├── app/                        # 应用主目录
│   ├── __init__.py            # 包初始化文件
│   │
│   ├── controllers/           # 控制层 (Controller)
│   │   ├── __init__.py
│   │   ├── base.py           # 基础控制器，提供统一的用户认证逻辑
│   │   ├── auth.py           # 鉴权控制器，处理登录、注册、退出
│   │   └── home.py           # 首页控制器
│   │
│   ├── models/                # 模型层 (Model)
│   │   ├── __init__.py
│   │   ├── db.py             # 数据库访问层，SQLite 连接和初始化
│   │   └── user.py           # 用户模型，用户相关数据库操作
│   │
│   ├── static/                # 静态资源
│   │   ├── css/
│   │   │   └── base.css      # 基础样式文件
│   │   ├── js/
│   │   │   └── base.js       # 基础 JavaScript 文件
│   │   └── dist/             # 前端组件库（本地化）
│   │       ├── bootstrap-5.3.8-dist/    # ✅ Bootstrap CSS框架（已解压）
│   │       ├── fontawesome-free-5.15.4-web/  # ✅ Font Awesome图标库（已解压）
│   │       └── layui/          # ✅ Layui UI框架（已解压）
│   │
│   └── templates/             # 视图层 (View)
│       ├── base.html         # 基础模板，定义页面骨架
│       ├── index.html        # 首页模板
│       ├── login.html        # 登录页模板
│       └── register.html     # 注册页模板
│
└── database/                  # 数据库目录
    └── app.db                # SQLite 数据库文件
```

## 已实现功能

### 1. 用户认证系统

#### 1.1 用户注册
- **路由**: `/register`
- **方法**: GET, POST
- **功能**:
  - 用户名唯一性验证
  - 密码确认验证
  - 使用 bcrypt 对密码进行哈希加密
  - 注册成功后自动登录并跳转到首页
- **文件**: [app/controllers/auth.py](app/controllers/auth.py) - RegisterHandler

#### 1.2 用户登录
- **路由**: `/login`
- **方法**: GET, POST
- **功能**:
  - 用户名和密码验证
  - 使用 bcrypt 验证密码哈希
  - 登录成功后设置安全 Cookie 并跳转到首页
- **文件**: [app/controllers/auth.py](app/controllers/auth.py) - LoginHandler

#### 1.3 用户退出
- **路由**: `/logout`
- **方法**: GET
- **功能**:
  - 清除用户登录态 Cookie
  - 重定向到登录页面
- **文件**: [app/controllers/auth.py](app/controllers/auth.py) - LogoutHandler

#### 1.4 首页访问控制
- **路由**: `/`
- **方法**: GET
- **功能**:
  - 检查用户登录状态
  - 未登录用户重定向到登录页
  - 已登录用户显示欢迎页面
- **文件**: [app/controllers/home.py](app/controllers/home.py) - HomeHandler

### 2. 数据库设计

#### users 表（用户表）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| username | TEXT | 用户名，唯一 |
| password_hash | TEXT | 密码哈希值 |
| created_at | TIMESTAMP | 创建时间 |

### 3. 安全特性
- 使用 bcrypt 进行密码哈希加密
- 使用 Tornado 的安全 Cookie 机制
- XSRF 保护（当前开发环境关闭，生产环境需开启）
- Cookie 密钥配置

## 待开发功能

根据 [requirements.md](requirements.md) 需求文档，以下功能待开发：

> **提示**: 详细的数据库表设计、功能清单、开发优先级等内容请参考 [requirements.md](requirements.md)

### 前端-用户侧

#### 1. 智能问数系统 🔴 高优先级
- [ ] 通过大模型提问功能
- [ ] 后台数据范围响应
- [ ] 数据存储容器支持
  - [ ] 文本存储
  - [ ] 数据库存储
  - [ ] 向量库存储

### 后端-管理侧

#### 2. 用户管理 🔴 高优先级
- [ ] 用户列表查看（分页、搜索）
- [ ] 用户信息编辑
- [ ] 用户删除/禁用
- [ ] 用户权限分配
- [ ] 用户登录日志

#### 3. 功能管理 🔴 高优先级
- [ ] 功能模块配置
- [ ] 功能开关控制
- [ ] 模块启用/禁用状态管理

#### 4. 权限管理 🔴 高优先级
- [ ] 角色管理（管理员、普通用户等）
- [ ] 权限分配
- [ ] 访问控制（RBAC）
- [ ] 权限组管理

#### 5. 数字员工 🟡 中优先级
- [ ] 数据查询员工
- [ ] 天气查询员工
- [ ] 新闻推送员工
- [ ] 音乐推荐员工
- [ ] 电影推荐员工

#### 6. 模型引擎 🔴 高优先级
- [ ] 动态模型切换（支持多个 AI 模型）
- [ ] 本地私有化模型支持
- [ ] 远程云端模型支持（OpenAI API 等）
- [ ] Token 统计功能
- [ ] 接口服务管理
- [ ] 流式响应配置（SSE）
- [ ] 模型调用日志

#### 7. 瞭望管理 🟡 中优先级
- [ ] 瞭望源动态管理
- [ ] 请求伪造技术应用（CSRF/SSRF）
- [ ] 采集数据批量处理
- [ ] 采集任务调度
- [ ] 采集结果存储

#### 8. 数据仓库 🟡 中优先级
- [ ] 非关系型数据库存储（MongoDB）
- [ ] 关系型数据库存储（MySQL/PostgreSQL）
- [ ] 向量库存储（Milvus/Faiss）
- [ ] 数据源配置管理
- [ ] 数据迁移工具

#### 9. 深度采集 🟢 低优先级
- [ ] 网页深度爬取
- [ ] 数据清洗处理
- [ ] 数据结构化存储
- [ ] 增量采集
- [ ] 增量更新检测

#### 10. 接口管理 🟢 低优先级
- [ ] API 接口配置
- [ ] 接口权限控制
- [ ] 接口调用统计
- [ ] 请求限流
- [ ] 接口文档自动生成

#### 11. 数智大屏 🟢 低优先级
- [ ] 平面炫酷展示
  - [ ] 报表组件开发（ECharts）
  - [ ] 动态数据展示
  - [ ] 实时数据刷新
- [ ] 数字孪生
  - [ ] 3D Web 开发（Three.js/WebGL）
  - [ ] GPU 渲染优化

#### 12. 系统设置 🟡 中优先级
- [ ] 系统参数配置
- [ ] 日志管理
- [ ] 邮件/短信配置
- [ ] 备份管理

#### 13. 系统统计 🟢 低优先级
- [ ] 用户统计（注册数、活跃度）
- [ ] 访问统计（PV/UV）
- [ ] 功能使用统计
- [ ] 数据增长统计
- [ ] Token 消耗统计

## 核心模块说明

### 1. 主入口模块 (app.py)

**功能**: Tornado 应用启动和路由配置

**关键代码**:
```python
def make_app():
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "app", "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "app", "static"),
        "cookie_secret": "your-cookie-secret-key-change-in-production",
        "login_url": "/login",
        "xsrf_cookies": False,   # 开发方便，生产环境应开启
        "debug": True,
    }
    return tornado.web.Application([
        (r"/", HomeHandler),
        (r"/register", RegisterHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
    ], **settings)
```

**配置说明**:
- `template_path`: 模板文件路径
- `static_path`: 静态资源路径
- `cookie_secret`: Cookie 加密密钥（生产环境需更换）
- `login_url`: 登录页面 URL
- `xsrf_cookies`: XSRF 保护开关
- `debug`: 调试模式开关

### 2. 基础控制器 (app/controllers/base.py)

**功能**: 提供统一的用户认证逻辑

**关键方法**:
- `get_current_user()`: 获取当前登录用户信息
- `get_current_user_name()`: 获取当前用户名

**使用方式**: 其他控制器继承 BaseHandler 即可使用用户认证功能

### 3. 鉴权控制器 (app/controllers/auth.py)

**功能**: 处理用户认证相关请求

**包含处理器**:
- `RegisterHandler`: 用户注册
- `LoginHandler`: 用户登录
- `LogoutHandler`: 用户退出

### 4. 数据库访问层 (app/models/db.py)

**功能**: SQLite 数据库连接和初始化

**关键函数**:
- `get_db()`: 获取数据库连接
- `init_db()`: 初始化数据库表结构

**数据库配置**:
- 数据库文件: `database/app.db`
- 使用 `sqlite3.Row` 返回字典形式的结果

### 5. 用户模型 (app/models/user.py)

**功能**: 用户相关数据库操作

**关键方法**:
- `create(username, password_hash)`: 创建用户
- `get_by_id(user_id)`: 根据 ID 获取用户
- `get_by_username(username)`: 根据用户名获取用户

## 开发指南

### 环境准备

#### 1. 安装 Python 3.12
确保系统已安装 Python 3.12 版本

#### 2. 安装依赖
```bash
pip install tornado==6.5.5
pip install bcrypt
```

#### 3. 运行项目
```bash
python app.py
```

#### 4. 访问应用
打开浏览器访问: http://localhost:8888

### 开发规范

#### 1. 目录结构规范
- **控制器**: 放置在 `app/controllers/` 目录
- **模型**: 放置在 `app/models/` 目录
- **模板**: 放置在 `app/templates/` 目录
- **静态资源**: 放置在 `app/static/` 目录

#### 2. 命名规范
- **控制器**: 使用 `XxxHandler` 命名，如 `UserHandler`
- **模型**: 使用 `XxxModel` 命名，如 `UserModel`
- **模板**: 使用小写命名，如 `user_list.html`
- **静态资源**: 使用小写命名，如 `user.css`

#### 3. 代码规范
- 使用 4 个空格缩进
- 类名使用大驼峰命名法
- 函数名使用小写加下划线命名法
- 添加必要的注释和文档字符串

#### 4. 数据库规范
- 表名使用复数形式，如 `users`
- 字段名使用小写加下划线，如 `created_at`
- 主键统一使用 `id`
- 时间字段使用 `TIMESTAMP` 类型

### 添加新功能步骤

#### 1. 创建数据库表
在 `app/models/db.py` 的 `init_db()` 函数中添加表创建语句

#### 2. 创建模型类
在 `app/models/` 目录下创建对应的模型文件，如 `article.py`

#### 3. 创建控制器
在 `app/controllers/` 目录下创建对应的控制器文件，如 `article.py`

#### 4. 创建模板
在 `app/templates/` 目录下创建对应的模板文件，如 `article_list.html`

#### 5. 配置路由
在 `app.py` 的路由列表中添加新的路由映射

#### 6. 创建静态资源（如需要）
在 `app/static/` 目录下创建对应的 CSS/JS 文件

### 示例：添加文章管理功能

#### 1. 数据库表
```python
# app/models/db.py
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        author_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES users (id)
    )
''')
```

#### 2. 模型类
```python
# app/models/article.py
from app.models.db import get_db

class ArticleModel:
    @staticmethod
    def create(title, content, author_id):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO articles (title, content, author_id) VALUES (?, ?, ?)",
                (title, content, author_id)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("创建文章失败:", e)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
```

#### 3. 控制器
```python
# app/controllers/article.py
from app.controllers.base import BaseHandler
from app.models.article import ArticleModel

class ArticleListHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect("/login")
            return
        articles = ArticleModel.get_all()
        self.render("article_list.html", articles=articles, username=user['username'])
```

#### 4. 路由配置
```python
# app.py
from app.controllers.article import ArticleListHandler

def make_app():
    return tornado.web.Application([
        # ... 其他路由
        (r"/articles", ArticleListHandler),
    ], **settings)
```

## API 接口说明

### 认证接口

#### 1. 用户注册
- **URL**: `/register`
- **方法**: POST
- **参数**:
  - `username`: 用户名
  - `password`: 密码
  - `confirm_password`: 确认密码
- **响应**: 注册成功后跳转到首页

#### 2. 用户登录
- **URL**: `/login`
- **方法**: POST
- **参数**:
  - `username`: 用户名
  - `password`: 密码
- **响应**: 登录成功后跳转到首页

#### 3. 用户退出
- **URL**: `/logout`
- **方法**: GET
- **响应**: 退出后跳转到登录页

### 页面接口

#### 1. 首页
- **URL**: `/`
- **方法**: GET
- **权限**: 需要登录
- **响应**: 显示欢迎页面

## 部署说明

### 开发环境部署

```bash
# 1. 克隆项目
git clone <项目地址>

# 2. 进入项目目录
cd cnAgentOS

# 3. 安装依赖
pip install tornado==6.5.5
pip install bcrypt

# 4. 运行项目
python app.py

# 5. 访问应用
# 浏览器打开 http://localhost:8888
```

### 生产环境部署

#### 1. 修改配置
```python
# app.py
settings = {
    # ...
    "cookie_secret": "生产环境强密钥",  # 更换为强密钥
    "xsrf_cookies": True,  # 开启 XSRF 保护
    "debug": False,  # 关闭调试模式
}
```

#### 2. 使用 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. 使用 Supervisor 守护进程
```ini
[program:cnagentos]
command=python /path/to/cnAgentOS/app.py
directory=/path/to/cnAgentOS
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/cnagentos.log
```

## 测试说明

### 单元测试
使用 `test.py` 文件进行单元测试

```python
# test.py 示例
import unittest
from app.models.user import UserModel

class TestUserModel(unittest.TestCase):
    def test_create_user(self):
        # 测试用户创建
        pass
    
    def test_get_user(self):
        # 测试用户查询
        pass

if __name__ == '__main__':
    unittest.main()
```

### 运行测试
```bash
python test.py
```

## 常见问题

### 1. 数据库文件不存在
**问题**: 运行时提示数据库文件不存在
**解决**: 首次运行时会自动创建数据库和表，确保 `database/` 目录存在

### 2. Cookie 安全警告
**问题**: 提示 Cookie 密钥不安全
**解决**: 在生产环境中更换 `cookie_secret` 为强密钥

### 3. 端口被占用
**问题**: 8888 端口已被占用
**解决**: 修改 `app.py` 中的端口号，或关闭占用端口的程序

### 4. 模板找不到
**问题**: 提示模板文件不存在
**解决**: 检查 `template_path` 配置是否正确，确保模板文件在正确位置

## 技术要点

### 1. Tornado 框架特点
- 高性能异步 Web 框架
- 内置模板引擎
- 支持 WebSocket
- 支持异步 I/O

### 2. MVC 架构优势
- 分层清晰，职责明确
- 便于维护和扩展
- 代码复用性高
- 易于测试

### 3. bcrypt 密码加密
- 使用 Blowfish 算法
- 自动加盐
- 防止彩虹表攻击
- 安全性高

### 4. SQLite 数据库
- 轻量级，无需安装
- 单文件存储，便于备份
- 适合中小型应用
- 可平滑迁移到 MySQL/PostgreSQL

## 后续开发建议

### 1. 优先级排序
1. **高优先级**: 用户管理、权限管理、模型引擎
2. **中优先级**: 数字员工、数据仓库、瞭望管理
3. **低优先级**: 数智大屏、深度采集、接口管理

### 2. 技术选型建议
- **向量数据库**: Milvus 或 Faiss
- **非关系数据库**: MongoDB
- **关系数据库**: MySQL 或 PostgreSQL
- **前端框架**: Vue.js 或 React（如需复杂交互）
- **3D 渲染**: Three.js（数智大屏）
- **大模型**: OpenAI API 或本地部署 LLaMA

### 3. 安全建议
- 开启 XSRF 保护
- 使用 HTTPS
- 实施请求频率限制
- 添加日志记录和监控
- 定期安全审计

### 4. 性能优化建议
- 使用连接池
- 添加缓存机制（Redis）
- 异步处理耗时任务
- 数据库索引优化
- 静态资源 CDN 加速

## 版本历史

### v0.1.0 (当前版本)
- 实现用户注册功能
- 实现用户登录功能
- 实现用户退出功能
- 实现首页访问控制
- 完成基础 MVC 架构搭建

## 许可证

待定

## 联系方式

待补充

---

**文档生成时间**: 2026-05-23

**文档版本**: v1.0

**注意**: 本文档基于当前项目代码和需求文档生成，用于指导后续开发工作。开发过程中请根据实际情况更新本文档。
