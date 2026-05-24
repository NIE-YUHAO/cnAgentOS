import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../database/app.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表，在第一次运行时调用"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'admin',
            status INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER DEFAULT 0,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            type TEXT DEFAULT 'menu',
            icon TEXT,
            url TEXT,
            sort_order INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            is_super INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            function_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (function_id) REFERENCES functions(id),
            UNIQUE(role_id, function_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES admin_users(id),
            FOREIGN KEY (role_id) REFERENCES roles(id),
            UNIQUE(admin_id, role_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            api_type TEXT DEFAULT 'openai',
            api_base TEXT,
            api_key TEXT,
            model_name TEXT,
            max_tokens INTEGER DEFAULT 4096,
            temperature REAL DEFAULT 0.7,
            top_p REAL DEFAULT 1.0,
            description TEXT,
            is_default INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            prompt_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            usage_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS observation_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            source_type TEXT NOT NULL,
            entry_url TEXT NOT NULL,
            request_method TEXT DEFAULT 'GET',
            headers TEXT,
            params_template TEXT,
            encoding TEXT DEFAULT 'utf-8',
            parse_rule TEXT,
            status INTEGER DEFAULT 1,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_interfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            api_url TEXT NOT NULL,
            request_method TEXT DEFAULT 'GET',
            response_format TEXT DEFAULT 'JSON',
            description TEXT,
            parameters TEXT,
            example TEXT,
            qps_limit INTEGER DEFAULT 4,
            token_required INTEGER DEFAULT 0,
            category TEXT DEFAULT 'other',
            status INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS digital_workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            alias TEXT UNIQUE NOT NULL,
            worker_type TEXT NOT NULL,
            description TEXT,
            avatar TEXT,
            prompt TEXT,
            model_id INTEGER,
            api_interface_id INTEGER,
            response_mode TEXT DEFAULT 'text',
            is_default INTEGER DEFAULT 0,
            status INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models(id),
            FOREIGN KEY (api_interface_id) REFERENCES api_interfaces(id)
        )
    ''')

    init_default_observation_sources(cursor)
    init_default_api_interfaces(cursor)
    init_default_models(cursor)
    init_default_digital_workers(cursor)

    cursor.execute('SELECT COUNT(*) FROM admin_users WHERE username = ?', ('admin',))
    count = cursor.fetchone()[0]
    if count == 0:
        import bcrypt
        password_hash = bcrypt.hashpw('admin888'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('''
            INSERT INTO admin_users (username, password_hash, email, role, status)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', password_hash, 'admin@example.com', 'admin', 1))

    cursor.execute('SELECT COUNT(*) FROM roles WHERE code = ?', ('super_admin',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO roles (name, code, description, is_super, status)
            VALUES (?, ?, ?, ?, ?)
        ''', ('超级管理员', 'super_admin', '系统超级管理员，拥有所有权限', 1, 1))

        cursor.execute('SELECT id FROM roles WHERE code = ?', ('super_admin',))
        super_role_id = cursor.fetchone()[0]

        cursor.execute('SELECT id FROM admin_users WHERE username = ?', ('admin',))
        admin_user = cursor.fetchone()
        if admin_user:
            cursor.execute('INSERT INTO admin_roles (admin_id, role_id) VALUES (?, ?)', (admin_user[0], super_role_id))

    init_default_functions(cursor)

    conn.commit()
    conn.close()

def init_default_functions(cursor):
    """初始化默认功能菜单"""
    cursor.execute('SELECT COUNT(*) FROM functions')
    if cursor.fetchone()[0] > 0:
        return

    import time
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    default_functions = [
        (0, '系统管理', 'system', 'directory', 'layui-icon-set', '#', 1, 1, now, now),
        (0, '模型引擎', 'model', 'directory', 'layui-icon-engine', '#', 2, 1, now, now),
        (0, '瞭望管理', 'watch', 'directory', 'layui-icon-eye', '#', 3, 1, now, now),
        (0, '数字员工', 'worker', 'directory', 'layui-icon-robot', '#', 4, 1, now, now),
        (0, '数智大屏', 'screen', 'directory', 'layui-icon-screen', '#', 5, 1, now, now),
        (1, '用户管理', 'system:user', 'menu', 'layui-icon-user', '/admin/user', 101, 1, now, now),
        (1, '功能管理', 'system:function', 'menu', 'layui-icon-app', '/admin/function', 102, 1, now, now),
        (1, '角色管理', 'system:role', 'menu', 'layui-icon-group', '/admin/role', 103, 1, now, now),
        (1, '权限管理', 'system:permission', 'menu', 'layui-icon-transfer', '/admin/permission', 104, 1, now, now),
        (1, '操作日志', 'system:log', 'menu', 'layui-icon-file', '#', 105, 1, now, now),
        (1, '接口管理', 'system:api', 'menu', 'layui-icon-release', '/admin/api_interface', 106, 1, now, now),
        (2, '模型管理', 'model:list', 'menu', 'layui-icon-server', '#', 201, 1, now, now),
        (2, 'Token统计', 'model:token', 'menu', 'layui-icon-chart-screen', '#', 202, 1, now, now),
        (3, '瞭望源管理', 'watch:source', 'menu', 'layui-icon-link', '/admin/observation', 301, 1, now, now),
        (3, '采集任务', 'watch:task', 'menu', 'layui-icon-clock', '#', 302, 1, now, now),
        (4, '数据查询员工', 'worker:query', 'menu', 'layui-icon-search', '#', 401, 1, now, now),
        (4, '天气查询员工', 'worker:weather', 'menu', 'layui-icon-weather', '#', 402, 1, now, now),
        (4, '新闻推送员工', 'worker:news', 'menu', 'layui-icon-read', '#', 403, 1, now, now),
        (5, '数据报表', 'screen:report', 'menu', 'layui-icon-chart', '#', 501, 1, now, now),
        (5, '数字孪生', 'screen:twins', 'menu', 'layui-icon-3d', '#', 502, 1, now, now),
    ]

    for func in default_functions:
        cursor.execute('''
            INSERT INTO functions (parent_id, name, code, type, icon, url, sort_order, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', func)

def init_default_observation_sources(cursor):
    """初始化默认观察数据源"""
    cursor.execute('SELECT COUNT(*) FROM observation_sources')
    if cursor.fetchone()[0] > 0:
        return

    import time
    import json
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    baidu_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "www.baidu.com",
        "Referer": "https://news.baidu.com/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.8.5161 SLBChan/111 SLBVPV/64-bit"
    }

    default_sources = [
        {
            'name': '百度新闻',
            'code': 'baidu_news',
            'source_type': 'news',
            'entry_url': 'https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={keyword}',
            'request_method': 'GET',
            'headers': json.dumps(baidu_headers, ensure_ascii=False),
            'params_template': json.dumps({'keyword': ''}, ensure_ascii=False),
            'encoding': 'utf-8',
            'parse_rule': json.dumps({
                'type': 'xpath',
                'selector': '//div[@class="news-wrap"]//h3/a|//div[@class="c-title"]/a',
                'title': './/text()',
                'url': './@href'
            }, ensure_ascii=False),
            'description': '百度新闻搜索采集源，支持关键词搜索新闻',
            'status': 1
        },
    ]

    for source in default_sources:
        cursor.execute('''
            INSERT INTO observation_sources (name, code, source_type, entry_url, request_method, headers, params_template, encoding, parse_rule, description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            source['name'], source['code'], source['source_type'], source['entry_url'],
            source['request_method'], source['headers'], source['params_template'],
            source['encoding'], source['parse_rule'], source['description'],
            source['status'], now, now
        ))

def init_default_api_interfaces(cursor):
    """初始化默认API接口"""
    cursor.execute('SELECT COUNT(*) FROM api_interfaces')
    if cursor.fetchone()[0] > 0:
        return

    import time
    import json
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    default_apis = [
        {
            'name': '网易云音乐随机推荐',
            'code': 'music_wy_rand',
            'api_url': 'https://api.52vmy.cn/api/music/wy/rand',
            'request_method': 'GET',
            'response_format': 'JSON',
            'description': '随机推荐一首网易云音乐',
            'parameters': json.dumps([], ensure_ascii=False),
            'example': 'https://api.52vmy.cn/api/music/wy/rand',
            'qps_limit': 4,
            'token_required': 0,
            'category': 'music',
            'status': 1
        },
        {
            'name': '天行天气查询',
            'code': 'weather_tian',
            'api_url': 'https://api.52vmy.cn/api/query/tian',
            'request_method': 'GET',
            'response_format': 'JSON',
            'description': '查询指定城市三日天气情况',
            'parameters': json.dumps([
                {'name': 'city', 'type': 'string', 'required': True, 'description': '城市名称，如：北京市'}
            ], ensure_ascii=False),
            'example': 'https://api.52vmy.cn/api/query/tian?city=北京市',
            'qps_limit': 4,
            'token_required': 0,
            'category': 'weather',
            'status': 1
        },
    ]

    for api in default_apis:
        cursor.execute('''
            INSERT INTO api_interfaces (name, code, api_url, request_method, response_format, description, parameters, example, qps_limit, token_required, category, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            api['name'], api['code'], api['api_url'], api['request_method'],
            api['response_format'], api['description'], api['parameters'],
            api['example'], api['qps_limit'], api['token_required'],
            api['category'], api['status'], now, now
        ))

def init_default_digital_workers(cursor):
    """初始化默认数字员工"""
    cursor.execute('SELECT COUNT(*) FROM digital_workers')
    if cursor.fetchone()[0] > 0:
        return

    import time
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('SELECT id FROM models WHERE is_default = 1')
    model_row = cursor.fetchone()
    model_id = model_row['id'] if model_row else None

    cursor.execute('SELECT id FROM api_interfaces WHERE code = ?', ('weather_tian',))
    weather_api_row = cursor.fetchone()
    weather_api_id = weather_api_row['id'] if weather_api_row else None

    cursor.execute('SELECT id FROM api_interfaces WHERE code = ?', ('music_wy_rand',))
    music_api_row = cursor.fetchone()
    music_api_id = music_api_row['id'] if music_api_row else None

    default_workers = [
        {
            'name': '川小农',
            'alias': '川小农',
            'worker_type': 'AI',
            'description': '智能对话助手，基于大模型提供智能问答服务',
            'avatar': '/static/images/avatar/ai.png',
            'prompt': '你是一个友好、专业的AI助手，名叫"川小农"。你的任务是帮助用户解决问题，提供准确、有用的信息。请用简洁、友好的语气回答问题。',
            'model_id': model_id,
            'api_interface_id': None,
            'response_mode': 'sse',
            'is_default': 1,
            'status': 1
        },
        {
            'name': '天气助手',
            'alias': '天气',
            'worker_type': '普通',
            'description': '天气查询助手，提供城市天气信息查询服务，用户通过@天气+城市名获取天气数据',
            'avatar': '/static/images/avatar/weather.png',
            'prompt': None,
            'model_id': None,
            'api_interface_id': weather_api_id,
            'response_mode': 'json',
            'is_default': 0,
            'status': 1
        },
        {
            'name': '音乐助手',
            'alias': '音乐',
            'worker_type': '普通',
            'description': '音乐推荐助手，提供随机音乐推荐服务，用户通过@音乐获取随机音乐卡片',
            'avatar': '/static/images/avatar/music.png',
            'prompt': None,
            'model_id': None,
            'api_interface_id': music_api_id,
            'response_mode': 'json',
            'is_default': 0,
            'status': 1
        },
    ]

    for worker in default_workers:
        cursor.execute('''
            INSERT INTO digital_workers (name, alias, worker_type, description, avatar, prompt, model_id, api_interface_id, response_mode, is_default, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            worker['name'], worker['alias'], worker['worker_type'], worker['description'],
            worker['avatar'], worker['prompt'], worker['model_id'], worker['api_interface_id'],
            worker['response_mode'], worker['is_default'], worker['status'], now, now
        ))

def init_default_models(cursor):
    """初始化默认模型"""
    cursor.execute('SELECT COUNT(*) FROM models')
    if cursor.fetchone()[0] > 0:
        return

    import time
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    default_models = [
        ('DeepSeek-V3', 'deepseek-v3', 'openai', 'https://aigc-api.aitoolcore.com/api/v1', 
         'sk-aigc-ccc9d8b95e5673fec23272d26b73ca940002520f', 'deepseek-v3', 
         8192, 0.7, 1.0, 'DeepSeek R1 V3 大语言模型，支持中文对话', 1, 1, now, now),
        ('DeepSeek-Chat', 'deepseek-chat', 'openai', 'https://aigc-api.aitoolcore.com/api/v1', 
         'sk-aigc-ccc9d8b95e5673fec23272d26b73ca940002520f', 'deepseek-chat', 
         4096, 0.7, 1.0, 'DeepSeek Chat 对话模型', 0, 1, now, now),
    ]

    for model in default_models:
        cursor.execute('''
            INSERT INTO models (name, code, api_type, api_base, api_key, model_name,
                               max_tokens, temperature, top_p, description,
                               is_default, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', model)

init_db()