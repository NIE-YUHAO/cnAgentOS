# 需求文档

> **文档版本**: v1.2
> **最后更新**: 2026-05-23
> **维护状态**: 由人类和 AI 共同维护

---

## 技术栈配置

### 前端组件库（本地化 - 已配置）

| 组件名称 | 版本 | 路径 | 说明 |
|---------|------|------|------|
| Bootstrap | 5.3.8 | `app/static/dist/bootstrap-5.3.8-dist/` | ✅ **已解压** - CSS 框架，用于响应式布局和 UI 组件 |
| Font Awesome | 5.15.4 | `app/static/dist/fontawesome-free-5.15.4-web/` | ✅ **已解压** - 图标库，提供丰富的矢量图标 |
| Layui | 2.13.6 | `app/static/dist/layui/layui-v2.13.6/layui/` | ✅ **已解压** - 轻量级前端 UI 框架 |

> **重要提示**: 所有前端组件必须本地化使用，禁止引用互联网资源。三大前端组件库均已就绪，可以开始使用。

### 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.12 | 编程语言 |
| Tornado | 6.5.5 | Web 框架 |
| SQLite3 | 内置 | 关系型数据库 |
| bcrypt | 最新 | 密码加密 |

---

## 功能需求

### 一、前端-用户侧

#### 1. 登录/注册/问数系统

**优先级**: 🔴 高

**功能描述**:
- 用户注册功能（已完成）
- 用户登录功能（已完成）
- **智能问数功能**（待开发）
  - 通过大模型提问，后台根据数据范围响应用户问题
  - 支持流式响应展示

**数据存储容器**:
| 容器类型 | 状态 | 说明 |
|---------|------|------|
| 文本存储 | 待开发 | 支持文本数据存储和检索 |
| 数据库存储 | 已基础 | SQLite 已配置，可扩展 MySQL/PostgreSQL |
| 向量库存储 | 待开发 | 支持 Milvus/Faiss 向量数据库 |

---

### 二、后端-管理侧

#### 2. 用户管理

**优先级**: 🔴 高

**功能清单**:
- [ ] 用户列表查看（分页、搜索）
- [ ] 用户信息编辑
- [ ] 用户删除/禁用
- [ ] 用户权限分配
- [ ] 用户登录日志

**数据库表设计**:
```sql
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

#### 3. 功能管理

**优先级**: 🔴 高

**功能清单**:
- [ ] 功能模块配置
- [ ] 功能开关控制
- [ ] 模块启用/禁用状态管理

**数据库表设计**:
```sql
CREATE TABLE IF NOT EXISTS features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_code TEXT UNIQUE NOT NULL,
    feature_name TEXT NOT NULL,
    description TEXT,
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

#### 4. 权限管理

**优先级**: 🔴 高

**功能清单**:
- [ ] 角色管理（管理员、普通用户等）
- [ ] 权限分配
- [ ] 访问控制（基于角色的访问控制 RBAC）
- [ ] 权限组管理

**数据库表设计**:
```sql
-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    permission_code TEXT UNIQUE NOT NULL,
    permission_name TEXT NOT NULL,
    resource TEXT,
    action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER,
    permission_id INTEGER,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES admin_users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
```

---

#### 5. 数字员工

**优先级**: 🟡 中

**功能清单**:
- [ ] 数据查询员工
- [ ] 天气查询员工
- [ ] 新闻推送员工
- [ ] 音乐推荐员工
- [ ] 电影推荐员工

**数据库表设计**:
```sql
CREATE TABLE IF NOT EXISTS digital_employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_code TEXT UNIQUE NOT NULL,
    employee_name TEXT NOT NULL,
    employee_type TEXT NOT NULL,
    description TEXT,
    config TEXT,
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

**员工类型说明**:
- `data`: 数据查询员工
- `weather`: 天气查询员工
- `news`: 新闻推送员工
- `music`: 音乐推荐员工
- `movie`: 电影推荐员工

---

#### 6. 模型引擎

**优先级**: 🔴 高

**功能清单**:
- [ ] 动态模型切换（支持多个 AI 模型）
- [ ] 本地私有化模型支持
- [ ] 远程云端模型支持（OpenAI API 等）
- [ ] Token 统计功能
- [ ] 接口服务管理
- [ ] 配置-流式响应（SSE）
- [ ] 模型调用日志

**数据库表设计**:
```sql
-- 模型配置表
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_code TEXT UNIQUE NOT NULL,
    model_name TEXT NOT NULL,
    model_type TEXT NOT NULL,
    endpoint TEXT,
    api_key TEXT,
    model_params TEXT,
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 模型类型: local(本地), remote(远程)

-- Token 使用统计表
CREATE TABLE IF NOT EXISTS token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    model_id INTEGER,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES admin_users(id),
    FOREIGN KEY (model_id) REFERENCES models(id)
);
```

---

#### 7. 瞭望管理

**优先级**: 🟡 中

**功能清单**:
- [ ] 瞭望源动态管理
- [ ] 请求伪造技术应用
  - CSRF（跨站请求伪造）防护/测试
  - SSRF（服务器端请求伪造）防护/测试
- [ ] 采集数据批量处理
- [ ] 采集任务调度
- [ ] 采集结果存储

**数据库表设计**:
```sql
-- 瞭望源表
CREATE TABLE IF NOT EXISTS watch_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_code TEXT UNIQUE NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_type TEXT,
    request_method TEXT DEFAULT 'GET',
    headers TEXT,
    body_template TEXT,
    response_parser TEXT,
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 采集任务表
CREATE TABLE IF NOT EXISTS watch_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_code TEXT UNIQUE NOT NULL,
    task_name TEXT NOT NULL,
    source_id INTEGER,
    schedule_type TEXT,
    cron_expression TEXT,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES watch_sources(id)
);

-- 采集结果表
CREATE TABLE IF NOT EXISTS watch_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    source_id INTEGER,
    data_content TEXT,
    data_snapshot TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES watch_tasks(id),
    FOREIGN KEY (source_id) REFERENCES watch_sources(id)
);
```

---

#### 8. 数据仓库

**优先级**: 🟡 中

**功能清单**:
- [ ] 非关系型数据库存储（MongoDB）
- [ ] 关系型数据库存储（MySQL/PostgreSQL）
- [ ] 向量库存储（Milvus/Faiss）
- [ ] 数据源配置管理
- [ ] 数据迁移工具

**数据库表设计**:
```sql
-- 数据源配置表
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    connection_config TEXT,
    status INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 数据源类型: mongodb, mysql, postgresql, milvus, faiss, sqlite
```

---

#### 9. 深度采集

**优先级**: 🟢 低

**功能清单**:
- [ ] 网页深度爬取
- [ ] 数据清洗处理
- [ ] 数据结构化存储
- [ ] 增量采集
- [ ] 增量更新检测

---

#### 10. 接口管理

**优先级**: 🟢 低

**功能清单**:
- [ ] API 接口配置
- [ ] 接口权限控制
- [ ] 接口调用统计
- [ ] 请求限流
- [ ] 接口文档自动生成

**数据库表设计**:
```sql
-- API 接口表
CREATE TABLE IF NOT EXISTS api_endpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint_code TEXT UNIQUE NOT NULL,
    endpoint_path TEXT NOT NULL,
    method TEXT NOT NULL,
    description TEXT,
    requires_auth INTEGER DEFAULT 1,
    rate_limit INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API 调用日志表
CREATE TABLE IF NOT EXISTS api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint_id INTEGER,
    user_id INTEGER,
    request_method TEXT,
    request_path TEXT,
    request_params TEXT,
    response_status INTEGER,
    response_time INTEGER,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (endpoint_id) REFERENCES api_endpoints(id),
    FOREIGN KEY (user_id) REFERENCES admin_users(id)
);
```

---

#### 11. 数智大屏

**优先级**: 🟢 低

**功能清单**:
- [ ] 平面炫酷展示
  - [ ] 报表组件开发（ECharts）
  - [ ] 动态数据展示
  - [ ] 实时数据刷新
- [ ] 数字孪生
  - [ ] 3D Web 开发（Three.js/WebGL）
  - [ ] GPU 渲染优化

**技术选型**:
- 可视化图表: ECharts 5.x
- 3D 渲染: Three.js
- 动画效果: GSAP

---

#### 12. 系统设置

**优先级**: 🟡 中

**功能清单**:
- [ ] 系统参数配置
- [ ] 日志管理
- [ ] 邮件/短信配置
- [ ] 备份管理

**数据库表设计**:
```sql
-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT UNIQUE NOT NULL,
    config_value TEXT,
    config_type TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    resource TEXT,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES admin_users(id)
);
```

---

#### 13. 系统统计

**优先级**: 🟢 低

**功能清单**:
- [ ] 用户统计（注册数、活跃度）
- [ ] 访问统计（PV/UV）
- [ ] 功能使用统计
- [ ] 数据增长统计
- [ ] Token 消耗统计

**数据库表设计**:
```sql
-- 访问统计表
CREATE TABLE IF NOT EXISTS page_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    page_url TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 非功能需求

### 1. 安全性需求

- [ ] XSRF 保护（生产环境必须开启）
- [ ] SQL 注入防护
- [ ] XSS 防护
- [ ] 请求频率限制
- [ ] HTTPS 支持
- [ ] 敏感数据加密存储

### 2. 性能需求

- [ ] 数据库连接池
- [ ] 缓存机制（Redis）
- [ ] 异步任务队列
- [ ] 数据库索引优化
- [ ] API 响应时间 < 200ms

### 3. 可用性需求

- [ ] 错误页面定制
- [ ] 优雅降级
- [ ] 服务健康检查
- [ ] 自动备份

### 4. 可维护性需求

- [ ] 日志规范
- [ ] 代码注释规范
- [ ] API 文档
- [ ] 部署文档

---

## 开发优先级

### 第一阶段（核心功能）

1. 🔴 用户管理 - 完成用户相关功能
2. 🔴 权限管理 - RBAC 权限系统
3. 🔴 模型引擎 - AI 模型集成

### 第二阶段（主要功能）

4. 🟡 功能管理 - 功能模块配置
5. 🟡 数字员工 - 各类型员工开发
6. 🟡 瞭望管理 - 数据采集功能

### 第三阶段（扩展功能）

7. 🟢 数据仓库 - 多数据源支持
8. 🟢 接口管理 - API 管理功能
9. 🟢 系统设置 - 系统配置管理

### 第四阶段（高级功能）

10. 🟢 深度采集 - 数据爬取清洗
11. 🟢 数智大屏 - 数据可视化
12. 🟢 系统统计 - 数据统计分析

---

## 技术债务

- [ ] 清理未使用的依赖
- [ ] 优化数据库查询（N+1 问题）
- [ ] 添加单元测试覆盖率
- [ ] 完善错误处理
- [ ] 优化前端加载性能

---

## 备注

> **前端组件库状态**: ✅ 三大前端组件库（Bootstrap、Font Awesome、Layui）均已成功解压并就绪，可以开始使用。

> **文档维护**: 本文档由人类和 AI 共同维护，每次功能开发完成后请及时更新本文档。

> **版本控制**: 使用语义化版本号 v主版本.次版本.修订号

---

**文档更新记录**:

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-05-23 | v1.0 | 初始版本 | AI |
| 2026-05-23 | v1.1 | 完善需求说明，添加技术栈配置 | AI |
| 2026-05-23 | v1.2 | 成功解压 Bootstrap 和 Font Awesome，更新 layui 状态 | AI |
| 2026-05-23 | v1.3 | 成功解压 Layui 2.13.6，三大组件库全部就绪 | AI |
