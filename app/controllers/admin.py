import json
import tornado.web
from app.models.admin_user import AdminUserModel
from app.models.function import FunctionModel
from app.models.role import RoleModel
from app.models.permission import PermissionModel
from app.models.observation import ObservationSourceModel
from app.models.api_interface import ApiInterfaceModel
from app.models.digital_worker import DigitalWorkerModel
from app.models.model import ModelModel

class AdminBaseHandler(tornado.web.RequestHandler):
    """后台基础控制器，提供管理员认证"""

    def get_current_admin(self):
        """获取当前登录的管理员"""
        admin_id = self.get_secure_cookie("admin_id")
        if admin_id:
            return AdminUserModel.get_by_id(int(admin_id.decode('utf-8')))
        return None

    def prepare(self):
        """预处理，检查登录状态（除了登录页面）"""
        if self.request.path not in ['/admin/login'] and not self.get_current_admin():
            self.redirect('/admin/login')

    def write_json(self, data, status=200):
        """返回JSON响应"""
        self.set_header("Content-Type", "application/json")
        self.set_status(status)
        self.write(json.dumps(data))

class AdminLoginHandler(AdminBaseHandler):
    """管理员登录控制器"""

    def prepare(self):
        pass

    def get(self):
        """显示登录页面"""
        self.render("admin/login.html")

    def post(self):
        """处理登录请求"""
        username = self.get_argument('username', '').strip()
        password = self.get_argument('password', '').strip()

        if not username or not password:
            self.write_json({'code': 1, 'msg': '请输入用户名和密码'})
            return

        admin = AdminUserModel.get_by_username(username)

        if not admin:
            self.write_json({'code': 1, 'msg': '用户名不存在'})
            return

        if admin['status'] != 1:
            self.write_json({'code': 1, 'msg': '账号已被禁用'})
            return

        if not AdminUserModel.verify_password(admin, password):
            self.write_json({'code': 1, 'msg': '密码错误'})
            return

        self.set_secure_cookie("admin_id", str(admin['id']), expires_days=1)
        self.write_json({'code': 0, 'msg': '登录成功', 'data': {'redirect': '/admin'}})

class AdminIndexHandler(AdminBaseHandler):
    """后台首页控制器"""

    def get(self):
        """显示后台首页"""
        admin = self.get_current_admin()
        self.render("admin/index.html", admin=admin)

class AdminUserHandler(AdminBaseHandler):
    """管理员用户管理控制器"""

    def get(self):
        """显示用户管理页面"""
        admin = self.get_current_admin()
        roles = RoleModel.get_all()
        self.render("admin/user_list.html", admin=admin, roles=roles)

class AdminUserApiHandler(AdminBaseHandler):
    """管理员用户管理API"""

    def get(self):
        """获取用户列表（分页）"""
        page = int(self.get_argument('page', 1))
        page_size = int(self.get_argument('limit', 20))
        keyword = self.get_argument('keyword', '')

        result = AdminUserModel.get_list_with_role(page, page_size, keyword)
        self.write_json({
            'code': 0,
            'msg': 'success',
            'data': result['data'],
            'count': result['total']
        })

    def post(self):
        """新增用户"""
        username = self.get_argument('username', '').strip()
        password = self.get_argument('password', '').strip()
        email = self.get_argument('email', '').strip()
        role_id = int(self.get_argument('role_id', 0))
        status = int(self.get_argument('status', 1))

        if not username or not password:
            self.write_json({'code': 1, 'msg': '用户名和密码不能为空'})
            return

        if not role_id:
            self.write_json({'code': 1, 'msg': '请选择角色'})
            return

        existing = AdminUserModel.get_by_username(username)
        if existing:
            self.write_json({'code': 1, 'msg': '用户名已存在'})
            return

        user_id = AdminUserModel.create_with_role(username, password, email, role_id, status)
        if user_id:
            self.write_json({'code': 0, 'msg': '添加成功'})
        else:
            self.write_json({'code': 1, 'msg': '添加失败'})

    def put(self):
        """更新用户"""
        user_id = int(self.get_argument('id', 0))
        email = self.get_argument('email', '').strip()
        role_id = int(self.get_argument('role_id', 0))
        status = int(self.get_argument('status', 1))
        password = self.get_argument('password', '').strip()

        if not user_id:
            self.write_json({'code': 1, 'msg': '用户ID不能为空'})
            return

        user = AdminUserModel.get_by_id(user_id)
        if not user:
            self.write_json({'code': 1, 'msg': '用户不存在'})
            return

        if user['username'] == 'admin':
            if password:
                success = AdminUserModel.update_password(user_id, password)
                if success:
                    self.write_json({'code': 0, 'msg': '密码修改成功'})
                else:
                    self.write_json({'code': 1, 'msg': '密码修改失败'})
            else:
                self.write_json({'code': 1, 'msg': 'admin用户只能修改密码'})
            return

        data = {'email': email, 'status': status}
        if password:
            data['password'] = password

        success = AdminUserModel.update(user_id, **data)
        if success:
            if role_id:
                AdminUserModel.update_role(user_id, role_id)
            self.write_json({'code': 0, 'msg': '更新成功'})
        else:
            self.write_json({'code': 1, 'msg': '更新失败'})

    def delete(self):
        """删除用户"""
        ids = self.get_argument('ids', '')
        if not ids:
            self.write_json({'code': 1, 'msg': '请选择要删除的用户'})
            return

        id_list = [int(i) for i in ids.split(',')]

        for uid in id_list:
            user = AdminUserModel.get_by_id(uid)
            if user and user['username'] == 'admin':
                self.write_json({'code': 1, 'msg': '不能删除admin用户'})
                return

        current_admin = self.get_current_admin()
        if current_admin and current_admin['id'] in id_list:
            self.write_json({'code': 1, 'msg': '不能删除当前登录用户'})
            return

        count = AdminUserModel.batch_delete(id_list)
        if count > 0:
            self.write_json({'code': 0, 'msg': f'成功删除 {count} 个用户'})
        else:
            self.write_json({'code': 1, 'msg': '删除失败'})

class AdminFunctionHandler(AdminBaseHandler):
    """功能管理控制器"""

    def get(self):
        """显示功能管理页面"""
        admin = self.get_current_admin()
        self.render("admin/function_list.html", admin=admin)

class AdminFunctionApiHandler(AdminBaseHandler):
    """功能管理API"""

    def get(self):
        """获取功能列表"""
        action = self.get_argument('action', 'list')

        if action == 'tree':
            tree = FunctionModel.get_tree()
            self.write_json({'code': 0, 'msg': 'success', 'data': tree})
        else:
            page = int(self.get_argument('page', 1))
            page_size = int(self.get_argument('limit', 20))
            keyword = self.get_argument('keyword', '')
            result = FunctionModel.get_list(page, page_size, keyword)

            func_tree = FunctionModel.get_tree()
            for item in result['data']:
                if item['parent_id'] > 0:
                    parent = FunctionModel.get_by_id(item['parent_id'])
                    if parent:
                        item['parent_name'] = parent['name']

            self.write_json({
                'code': 0,
                'msg': 'success',
                'data': result['data'],
                'count': result['total']
            })

    def post(self):
        """新增功能"""
        parent_id = int(self.get_argument('parent_id', 0))
        name = self.get_argument('name', '').strip()
        code = self.get_argument('code', '').strip()
        type = self.get_argument('type', 'menu')
        icon = self.get_argument('icon', '')
        url = self.get_argument('url', '#')
        sort_order = int(self.get_argument('sort_order', 0))
        status = int(self.get_argument('status', 1))

        if not name or not code:
            self.write_json({'code': 1, 'msg': '功能名称和编码不能为空'})
            return

        existing = FunctionModel.get_by_code(code)
        if existing:
            self.write_json({'code': 1, 'msg': '功能编码已存在'})
            return

        func_id = FunctionModel.create(parent_id, name, code, type, icon, url, sort_order, status)
        if func_id:
            self.write_json({'code': 0, 'msg': '添加成功'})
        else:
            self.write_json({'code': 1, 'msg': '添加失败'})

    def put(self):
        """更新功能"""
        func_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '').strip()
        code = self.get_argument('code', '').strip()
        type = self.get_argument('type', 'menu')
        icon = self.get_argument('icon', '')
        url = self.get_argument('url', '#')
        sort_order = int(self.get_argument('sort_order', 0))
        status = int(self.get_argument('status', 1))

        if not func_id:
            self.write_json({'code': 1, 'msg': '功能ID不能为空'})
            return

        data = {
            'name': name,
            'code': code,
            'type': type,
            'icon': icon,
            'url': url,
            'sort_order': sort_order,
            'status': status
        }

        success = FunctionModel.update(func_id, **data)
        if success:
            self.write_json({'code': 0, 'msg': '更新成功'})
        else:
            self.write_json({'code': 1, 'msg': '更新失败'})

    def delete(self):
        """删除功能"""
        ids = self.get_argument('ids', '')
        if not ids:
            self.write_json({'code': 1, 'msg': '请选择要删除的功能'})
            return

        id_list = [int(i) for i in ids.split(',')]
        count = 0
        for func_id in id_list:
            if FunctionModel.delete(func_id):
                count += 1

        if count > 0:
            self.write_json({'code': 0, 'msg': f'成功删除 {count} 个功能'})
        else:
            self.write_json({'code': 1, 'msg': '删除失败'})

class AdminRoleHandler(AdminBaseHandler):
    """角色管理控制器"""

    def get(self):
        """显示角色管理页面"""
        admin = self.get_current_admin()
        self.render("admin/role_list.html", admin=admin)

class AdminRoleApiHandler(AdminBaseHandler):
    """角色管理API"""

    def get(self):
        """获取角色列表"""
        page = int(self.get_argument('page', 1))
        page_size = int(self.get_argument('limit', 20))
        keyword = self.get_argument('keyword', '')

        result = RoleModel.get_list(page, page_size, keyword)
        self.write_json({
            'code': 0,
            'msg': 'success',
            'data': result['data'],
            'count': result['total']
        })

    def post(self):
        """新增角色"""
        name = self.get_argument('name', '').strip()
        code = self.get_argument('code', '').strip()
        description = self.get_argument('description', '').strip()
        status = int(self.get_argument('status', 1))

        if not name or not code:
            self.write_json({'code': 1, 'msg': '角色名称和编码不能为空'})
            return

        existing = RoleModel.get_by_code(code)
        if existing:
            self.write_json({'code': 1, 'msg': '角色编码已存在'})
            return

        role_id = RoleModel.create(name, code, description, 0, status)
        if role_id:
            self.write_json({'code': 0, 'msg': '添加成功'})
        else:
            self.write_json({'code': 1, 'msg': '添加失败'})

    def put(self):
        """更新角色"""
        role_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '').strip()
        description = self.get_argument('description', '').strip()
        status = int(self.get_argument('status', 1))

        if not role_id:
            self.write_json({'code': 1, 'msg': '角色ID不能为空'})
            return

        role = RoleModel.get_by_id(role_id)
        if role and role['is_super'] == 1:
            self.write_json({'code': 1, 'msg': '超级管理员角色不能修改'})
            return

        data = {
            'name': name,
            'description': description,
            'status': status
        }

        success = RoleModel.update(role_id, **data)
        if success:
            self.write_json({'code': 0, 'msg': '更新成功'})
        else:
            self.write_json({'code': 1, 'msg': '更新失败'})

    def delete(self):
        """删除角色"""
        ids = self.get_argument('ids', '')
        if not ids:
            self.write_json({'code': 1, 'msg': '请选择要删除的角色'})
            return

        id_list = [int(i) for i in ids.split(',')]
        count = 0
        for role_id in id_list:
            if RoleModel.delete(role_id):
                count += 1

        if count > 0:
            self.write_json({'code': 0, 'msg': f'成功删除 {count} 个角色'})
        else:
            self.write_json({'code': 1, 'msg': '删除失败，超级管理员角色不能删除'})

class AdminPermissionHandler(AdminBaseHandler):
    """权限管理控制器"""

    def get(self):
        """显示权限管理页面"""
        import json
        admin = self.get_current_admin()
        roles = RoleModel.get_all()
        functions = FunctionModel.get_tree()
        functions_json = json.dumps(functions)
        self.render("admin/permission_list.html", admin=admin, roles=roles, functions=functions, functions_json=functions_json)

class AdminPermissionApiHandler(AdminBaseHandler):
    """权限管理API"""

    def get(self):
        """获取权限数据"""
        role_id = int(self.get_argument('role_id', 0))
        if role_id:
            permissions = PermissionModel.get_by_role(role_id)
            self.write_json({'code': 0, 'msg': 'success', 'data': permissions})
        else:
            self.write_json({'code': 1, 'msg': '请选择角色'})

    def post(self):
        """设置角色权限"""
        role_id = int(self.get_argument('role_id', 0))
        function_ids = self.get_arguments('function_ids')

        if not role_id:
            self.write_json({'code': 1, 'msg': '请选择角色'})
            return

        role = RoleModel.get_by_id(role_id)
        if role and role['is_super'] == 1:
            self.write_json({'code': 1, 'msg': '超级管理员拥有所有权限，无需设置'})
            return

        func_ids = [int(fid) for fid in function_ids]
        if PermissionModel.set_role_permissions(role_id, func_ids):
            self.write_json({'code': 0, 'msg': '权限设置成功'})
        else:
            self.write_json({'code': 1, 'msg': '权限设置失败'})

class AdminLogoutHandler(tornado.web.RequestHandler):
    """管理员退出登录"""
    def get(self):
        self.clear_cookie("admin_id")
        self.redirect("/admin/login")

class AdminObservationSourceHandler(AdminBaseHandler):
    """瞭望数据源管理控制器"""

    def get(self):
        """显示数据源管理页面"""
        admin = self.get_current_admin()
        self.render("admin/observation_source_list.html", admin=admin)

class AdminObservationSourceApiHandler(AdminBaseHandler):
    """瞭望数据源管理API"""

    def get(self):
        """获取数据源列表"""
        page = int(self.get_argument('page', 1))
        page_size = int(self.get_argument('limit', 10))
        keyword = self.get_argument('keyword', '')

        result = ObservationSourceModel.get_list(page, page_size, keyword)
        self.write_json({'code': 0, 'msg': 'success', 'data': result['data'], 'count': result['total']})

    def post(self):
        """创建数据源"""
        import json
        name = self.get_argument('name', '').strip()
        code = self.get_argument('code', '').strip()
        source_type = self.get_argument('source_type', '').strip()
        entry_url = self.get_argument('entry_url', '').strip()
        request_method = self.get_argument('request_method', 'GET').strip()
        headers_str = self.get_argument('headers', '').strip()
        params_template_str = self.get_argument('params_template', '').strip()
        encoding = self.get_argument('encoding', 'utf-8').strip()
        parse_rule_str = self.get_argument('parse_rule', '').strip()
        description = self.get_argument('description', '').strip()
        status = int(self.get_argument('status', 1))

        if not name or not code or not source_type or not entry_url:
            self.write_json({'code': 1, 'msg': '请填写必填字段'})
            return

        existing = ObservationSourceModel.get_by_code(code)
        if existing:
            self.write_json({'code': 1, 'msg': '数据源编码已存在'})
            return

        headers = json.loads(headers_str) if headers_str else None
        params_template = json.loads(params_template_str) if params_template_str else None
        parse_rule = json.loads(parse_rule_str) if parse_rule_str else None

        source_id = ObservationSourceModel.create(
            name, code, source_type, entry_url, request_method,
            headers, params_template, encoding, parse_rule, description, status
        )

        if source_id:
            self.write_json({'code': 0, 'msg': '创建成功'})
        else:
            self.write_json({'code': 1, 'msg': '创建失败'})

    def put(self):
        """更新数据源"""
        import json
        source_id = int(self.get_argument('id', 0))
        if not source_id:
            self.write_json({'code': 1, 'msg': '数据源ID不能为空'})
            return

        name = self.get_argument('name', '').strip()
        code = self.get_argument('code', '').strip()
        source_type = self.get_argument('source_type', '').strip()
        entry_url = self.get_argument('entry_url', '').strip()
        request_method = self.get_argument('request_method', 'GET').strip()
        headers_str = self.get_argument('headers', '').strip()
        params_template_str = self.get_argument('params_template', '').strip()
        encoding = self.get_argument('encoding', 'utf-8').strip()
        parse_rule_str = self.get_argument('parse_rule', '').strip()
        description = self.get_argument('description', '').strip()
        status = int(self.get_argument('status', 1))

        if not name or not code or not source_type or not entry_url:
            self.write_json({'code': 1, 'msg': '请填写必填字段'})
            return

        existing = ObservationSourceModel.get_by_code(code)
        if existing and existing['id'] != source_id:
            self.write_json({'code': 1, 'msg': '数据源编码已存在'})
            return

        headers = json.loads(headers_str) if headers_str else None
        params_template = json.loads(params_template_str) if params_template_str else None
        parse_rule = json.loads(parse_rule_str) if parse_rule_str else None

        ObservationSourceModel.update(
            source_id, name, code, source_type, entry_url, request_method,
            headers, params_template, encoding, parse_rule, description, status
        )
        self.write_json({'code': 0, 'msg': '更新成功'})

    def delete(self):
        """删除数据源"""
        source_id = int(self.get_argument('id', 0))
        if not source_id:
            self.write_json({'code': 1, 'msg': '数据源ID不能为空'})
            return

        if ObservationSourceModel.delete(source_id):
            self.write_json({'code': 0, 'msg': '删除成功'})
        else:
            self.write_json({'code': 1, 'msg': '删除失败'})

class AdminApiInterfaceHandler(AdminBaseHandler):
    """API接口管理控制器"""

    def get(self):
        """显示接口管理页面"""
        import json
        admin = self.get_current_admin()
        categories = ApiInterfaceModel.get_categories()
        categories_json = json.dumps(categories)
        self.render("admin/api_interface_list.html", admin=admin, categories=categories, categories_json=categories_json)

class AdminApiInterfaceApiHandler(AdminBaseHandler):
    """API接口管理API"""

    def get(self):
        """获取接口列表"""
        page = int(self.get_argument('page', 1))
        page_size = int(self.get_argument('limit', 10))
        keyword = self.get_argument('keyword', '')
        category = self.get_argument('category', '')

        result = ApiInterfaceModel.get_list(page, page_size, keyword, category)
        self.write_json({'code': 0, 'msg': 'success', 'data': result['data'], 'count': result['total']})

    def post(self):
        """创建接口"""
        import json
        name = self.get_argument('name', '').strip()
        code = self.get_argument('code', '').strip()
        api_url = self.get_argument('api_url', '').strip()
        request_method = self.get_argument('request_method', 'GET').strip()
        response_format = self.get_argument('response_format', 'JSON').strip()
        description = self.get_argument('description', '').strip()
        parameters_str = self.get_argument('parameters', '').strip()
        example = self.get_argument('example', '').strip()
        qps_limit = int(self.get_argument('qps_limit', 4))
        token_required = int(self.get_argument('token_required', 0))
        category = self.get_argument('category', 'other').strip()
        status = int(self.get_argument('status', 1))

        if not name or not code or not api_url:
            self.write_json({'code': 1, 'msg': '请填写必填字段'})
            return

        existing = ApiInterfaceModel.get_by_code(code)
        if existing:
            self.write_json({'code': 1, 'msg': '接口编码已存在'})
            return

        parameters = json.loads(parameters_str) if parameters_str else []

        interface_id = ApiInterfaceModel.create(
            name, code, api_url, request_method, response_format,
            description, parameters, example, qps_limit, token_required, category, status
        )

        if interface_id:
            self.write_json({'code': 0, 'msg': '创建成功'})
        else:
            self.write_json({'code': 1, 'msg': '创建失败'})

    def put(self):
        """更新接口"""
        import json
        interface_id = int(self.get_argument('id', 0))
        if not interface_id:
            self.write_json({'code': 1, 'msg': '接口ID不能为空'})
            return

        name = self.get_argument('name', '').strip()
        code = self.get_argument('code', '').strip()
        api_url = self.get_argument('api_url', '').strip()
        request_method = self.get_argument('request_method', 'GET').strip()
        response_format = self.get_argument('response_format', 'JSON').strip()
        description = self.get_argument('description', '').strip()
        parameters_str = self.get_argument('parameters', '').strip()
        example = self.get_argument('example', '').strip()
        qps_limit = int(self.get_argument('qps_limit', 4))
        token_required = int(self.get_argument('token_required', 0))
        category = self.get_argument('category', 'other').strip()
        status = int(self.get_argument('status', 1))

        if not name or not code or not api_url:
            self.write_json({'code': 1, 'msg': '请填写必填字段'})
            return

        existing = ApiInterfaceModel.get_by_code(code)
        if existing and existing['id'] != interface_id:
            self.write_json({'code': 1, 'msg': '接口编码已存在'})
            return

        parameters = json.loads(parameters_str) if parameters_str else []

        ApiInterfaceModel.update(
            interface_id, name, code, api_url, request_method, response_format,
            description, parameters, example, qps_limit, token_required, category, status
        )
        self.write_json({'code': 0, 'msg': '更新成功'})

    def delete(self):
        """删除接口"""
        interface_id = int(self.get_argument('id', 0))
        if not interface_id:
            self.write_json({'code': 1, 'msg': '接口ID不能为空'})
            return

        if ApiInterfaceModel.delete(interface_id):
            self.write_json({'code': 0, 'msg': '删除成功'})
        else:
            self.write_json({'code': 1, 'msg': '删除失败'})

class AdminDigitalWorkerHandler(AdminBaseHandler):
    """数字员工管理控制器"""

    def get(self):
        admin = self.get_current_admin()
        models = ModelModel.get_all(status=1)
        api_interfaces = ApiInterfaceModel.get_all(status=1)
        import json
        models_json = json.dumps([{'id': m['id'], 'name': m['name']} for m in models])
        api_interfaces_json = json.dumps([{'id': a['id'], 'name': a['name'], 'code': a['code']} for a in api_interfaces])
        self.render("admin/digital_worker_list.html", admin=admin, models=models,
                    api_interfaces=api_interfaces, models_json=models_json,
                    api_interfaces_json=api_interfaces_json)

class AdminDigitalWorkerApiHandler(AdminBaseHandler):
    """数字员工管理API"""

    def get(self):
        page = int(self.get_argument('page', 1))
        page_size = int(self.get_argument('limit', 10))
        keyword = self.get_argument('keyword', '')
        worker_type = self.get_argument('worker_type', '')

        result = DigitalWorkerModel.get_list(page, page_size, keyword, worker_type)
        data = result['data']

        for item in data:
            if item['model_id']:
                model = ModelModel.get_by_id(item['model_id'])
                item['model_name'] = model['name'] if model else ''
            else:
                item['model_name'] = ''

            if item['api_interface_id']:
                api = ApiInterfaceModel.get_by_id(item['api_interface_id'])
                item['api_name'] = api['name'] if api else ''
            else:
                item['api_name'] = ''

        self.write_json({'code': 0, 'msg': 'success', 'data': data, 'count': result['total']})

    def post(self):
        name = self.get_argument('name', '').strip()
        alias = self.get_argument('alias', '').strip()
        worker_type = self.get_argument('worker_type', '').strip()
        description = self.get_argument('description', '').strip()
        prompt = self.get_argument('prompt', '').strip()
        model_id = self.get_argument('model_id', '').strip()
        api_interface_id = self.get_argument('api_interface_id', '').strip()
        response_mode = self.get_argument('response_mode', 'text').strip()
        is_default = int(self.get_argument('is_default', 0))
        status = int(self.get_argument('status', 1))

        if not name or not alias or not worker_type:
            self.write_json({'code': 1, 'msg': '名称、别名和类别不能为空'})
            return

        existing = DigitalWorkerModel.get_by_alias(alias)
        if existing:
            self.write_json({'code': 1, 'msg': '别名已存在，请使用其他别名'})
            return

        model_id_val = int(model_id) if model_id else None
        api_interface_id_val = int(api_interface_id) if api_interface_id else None

        if worker_type == 'AI':
            if not model_id_val:
                self.write_json({'code': 1, 'msg': 'AI类型数字员工必须选择关联模型'})
                return
            if not prompt:
                self.write_json({'code': 1, 'msg': 'AI类型数字员工必须配置提示词'})
                return
            api_interface_id_val = None
            response_mode = 'sse'
        elif worker_type == '普通':
            if not api_interface_id_val:
                self.write_json({'code': 1, 'msg': '普通类型数字员工必须选择关联API接口'})
                return
            model_id_val = None
            prompt = ''
            response_mode = 'json'

        worker_id = DigitalWorkerModel.create(
            name, alias, worker_type, description, '', prompt,
            model_id_val, api_interface_id_val, response_mode,
            is_default, status
        )

        if worker_id:
            self.write_json({'code': 0, 'msg': '添加成功'})
        else:
            self.write_json({'code': 1, 'msg': '添加失败'})

    def put(self):
        worker_id = int(self.get_argument('id', 0))
        if not worker_id:
            self.write_json({'code': 1, 'msg': '数字员工ID不能为空'})
            return

        name = self.get_argument('name', '').strip()
        alias = self.get_argument('alias', '').strip()
        worker_type = self.get_argument('worker_type', '').strip()
        description = self.get_argument('description', '').strip()
        prompt = self.get_argument('prompt', '').strip()
        model_id = self.get_argument('model_id', '').strip()
        api_interface_id = self.get_argument('api_interface_id', '').strip()
        response_mode = self.get_argument('response_mode', 'text').strip()
        is_default = int(self.get_argument('is_default', 0))
        status = int(self.get_argument('status', 1))

        if not name or not alias or not worker_type:
            self.write_json({'code': 1, 'msg': '名称、别名和类别不能为空'})
            return

        existing = DigitalWorkerModel.get_by_alias(alias)
        if existing and existing['id'] != worker_id:
            self.write_json({'code': 1, 'msg': '别名已存在，请使用其他别名'})
            return

        model_id_val = int(model_id) if model_id else None
        api_interface_id_val = int(api_interface_id) if api_interface_id else None

        if worker_type == 'AI':
            if not model_id_val:
                self.write_json({'code': 1, 'msg': 'AI类型数字员工必须选择关联模型'})
                return
            if not prompt:
                self.write_json({'code': 1, 'msg': 'AI类型数字员工必须配置提示词'})
                return
            api_interface_id_val = None
            response_mode = 'sse'
        elif worker_type == '普通':
            if not api_interface_id_val:
                self.write_json({'code': 1, 'msg': '普通类型数字员工必须选择关联API接口'})
                return
            model_id_val = None
            prompt = ''
            response_mode = 'json'

        DigitalWorkerModel.update(
            worker_id, name, alias, worker_type, description, '',
            prompt, model_id_val, api_interface_id_val, response_mode,
            is_default, status
        )
        self.write_json({'code': 0, 'msg': '更新成功'})

    def delete(self):
        worker_id = int(self.get_argument('id', 0))
        if not worker_id:
            self.write_json({'code': 1, 'msg': '数字员工ID不能为空'})
            return

        if DigitalWorkerModel.delete(worker_id):
            self.write_json({'code': 0, 'msg': '删除成功'})
        else:
            self.write_json({'code': 1, 'msg': '删除失败'})