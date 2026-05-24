import tornado.web
import json
import time
from app.models.model import ModelModel, TokenUsageModel

class AdminModelHandler(tornado.web.RequestHandler):
    """模型管理控制器"""

    def get(self):
        """显示模型管理页面"""
        admin = self.get_secure_cookie("admin_id")
        self.render("admin/model_list.html", admin={'username': 'Admin'})

class AdminModelApiHandler(tornado.web.RequestHandler):
    """模型管理API"""

    def get(self):
        """获取模型列表（分页）"""
        page = int(self.get_argument('page', 1))
        page_size = int(self.get_argument('limit', 6))
        keyword = self.get_argument('keyword', '')

        result = ModelModel.get_list(page, page_size, keyword)
        self.write({
            'code': 0,
            'msg': 'success',
            'data': result['data'],
            'count': result['total']
        })

    def post(self):
        """新增模型"""
        name = self.get_argument('name', '').strip()
        code = self.get_argument('code', '').strip()
        api_type = self.get_argument('api_type', 'openai')
        api_base = self.get_argument('api_base', '').strip()
        api_key = self.get_argument('api_key', '').strip()
        model_name = self.get_argument('model_name', '').strip()
        max_tokens = int(self.get_argument('max_tokens', 4096))
        temperature = float(self.get_argument('temperature', 0.7))
        top_p = float(self.get_argument('top_p', 1.0))
        description = self.get_argument('description', '').strip()

        if not name or not code:
            self.write({'code': 1, 'msg': '名称和编码不能为空'})
            return

        existing = ModelModel.get_by_code(code)
        if existing:
            self.write({'code': 1, 'msg': '编码已存在'})
            return

        model_id = ModelModel.create(name, code, api_type, api_base, api_key, 
                                     model_name, max_tokens, temperature, top_p, description)
        if model_id:
            self.write({'code': 0, 'msg': '添加成功', 'data': {'id': model_id}})
        else:
            self.write({'code': 1, 'msg': '添加失败'})

    def put(self):
        """更新模型"""
        model_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '').strip()
        api_type = self.get_argument('api_type', 'openai')
        api_base = self.get_argument('api_base', '').strip()
        api_key = self.get_argument('api_key', '').strip()
        model_name = self.get_argument('model_name', '').strip()
        max_tokens = int(self.get_argument('max_tokens', 4096))
        temperature = float(self.get_argument('temperature', 0.7))
        top_p = float(self.get_argument('top_p', 1.0))
        description = self.get_argument('description', '').strip()
        status = int(self.get_argument('status', 1))

        if not model_id:
            self.write({'code': 1, 'msg': '模型ID不能为空'})
            return

        data = {
            'name': name,
            'api_type': api_type,
            'api_base': api_base,
            'api_key': api_key,
            'model_name': model_name,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'description': description,
            'status': status
        }

        success = ModelModel.update(model_id, **data)
        if success:
            self.write({'code': 0, 'msg': '更新成功'})
        else:
            self.write({'code': 1, 'msg': '更新失败'})

    def delete(self):
        """删除模型"""
        model_id = int(self.get_argument('id', 0))
        if not model_id:
            self.write({'code': 1, 'msg': '请选择要删除的模型'})
            return

        model = ModelModel.get_by_id(model_id)
        if model and model['is_default'] == 1:
            self.write({'code': 1, 'msg': '不能删除默认模型'})
            return

        if ModelModel.delete(model_id):
            self.write({'code': 0, 'msg': '删除成功'})
        else:
            self.write({'code': 1, 'msg': '删除失败'})

class AdminModelSetDefaultHandler(tornado.web.RequestHandler):
    """设置默认模型"""

    def post(self):
        model_id = int(self.get_argument('model_id', 0))
        if not model_id:
            self.write({'code': 1, 'msg': '请选择模型'})
            return

        if ModelModel.set_default(model_id):
            self.write({'code': 0, 'msg': '设置成功'})
        else:
            self.write({'code': 1, 'msg': '设置失败'})

class AdminModelTestHandler(tornado.web.RequestHandler):
    """模型测试控制器"""

    def get(self):
        model_id = int(self.get_argument('model_id', 0))
        model = ModelModel.get_by_id(model_id) if model_id else None
        models = ModelModel.get_all(status=1)
        self.render("admin/model_test.html", model=model, models=models)

class AdminModelTestApiHandler(tornado.web.RequestHandler):
    """模型测试API"""

    def post(self):
        model_id = int(self.get_argument('model_id', 0))
        message = self.get_argument('message', '').strip()
        stream = self.get_argument('stream', 'false').lower() == 'true'

        if not model_id or not message:
            self.write({'code': 1, 'msg': '请选择模型并输入消息'})
            return

        result, error = ModelModel.call_api(model_id, [{'role': 'user', 'content': message}], stream=False)
        
        if error:
            self.write({'code': 1, 'msg': error})
        elif result:
            choices = result.get('choices', [])
            if choices:
                content = choices[0].get('message', {}).get('content', '')
                self.write({'code': 0, 'msg': 'success', 'data': {'content': content}})
            else:
                self.write({'code': 1, 'msg': '模型返回为空'})
        else:
            self.write({'code': 1, 'msg': '调用失败'})

class AdminModelStreamHandler(tornado.web.RequestHandler):
    """模型流式响应API（SSE）"""

    def get(self):
        """GET方式支持EventSource调用"""
        model_id = int(self.get_argument('model_id', 0))
        message = self.get_argument('message', '').strip()
        self._stream_response(model_id, message)

    def post(self):
        """POST方式支持流式响应"""
        model_id = int(self.get_argument('model_id', 0))
        message = self.get_argument('message', '').strip()
        self._stream_response(model_id, message)

    def _stream_response(self, model_id, message):
        """处理流式响应"""
        if not model_id or not message:
            self.set_header('Content-Type', 'text/event-stream')
            self.write(f'data: {json.dumps({"code": 1, "msg": "请选择模型并输入消息"})}\n\n')
            self.finish()
            return

        result, error = ModelModel.call_api(model_id, [{'role': 'user', 'content': message}], stream=True)
        
        if error:
            self.set_header('Content-Type', 'text/event-stream')
            self.write(f'data: {json.dumps({"code": 1, "msg": error})}\n\n')
            self.finish()
            return

        self.set_header('Content-Type', 'text/event-stream')
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('Connection', 'keep-alive')
        self.set_header('Access-Control-Allow-Origin', '*')

        content = ''
        try:
            for line in result.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line_data = line[5:]
                        if line_data.strip() == '[DONE]':
                            continue
                        try:
                            data = json.loads(line_data)
                            choices = data.get('choices', [])
                            if choices:
                                delta = choices[0].get('delta', {})
                                if 'content' in delta:
                                    content += delta['content']
                                    self.write(f'data: {json.dumps({"code": 0, "content": delta["content"]})}\n\n')
                                    self.flush()
                                finish_reason = choices[0].get('finish_reason')
                                if finish_reason:
                                    self.write(f'data: {json.dumps({"code": 0, "content": "", "finish": True, "finish_reason": finish_reason})}\n\n')
                                    self.flush()
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            self.write(f'data: {json.dumps({"code": 1, "msg": str(e)})}\n\n')
            self.flush()
        finally:
            self.finish()

class AdminTokenStatsHandler(tornado.web.RequestHandler):
    """Token统计页面"""

    def get(self):
        admin_id = self.get_secure_cookie("admin_id")
        admin = {'username': 'Admin'} if admin_id else None
        models = ModelModel.get_all(status=1)
        self.render("admin/token_stats.html", models=models, admin=admin)

class AdminTokenStatsApiHandler(tornado.web.RequestHandler):
    """Token统计API"""

    def get(self):
        model_id = self.get_argument('model_id', '')
        days = int(self.get_argument('days', 7))

        if model_id:
            data = TokenUsageModel.get_by_model(int(model_id), days)
        else:
            data = TokenUsageModel.get_daily_summary(days)

        self.write({'code': 0, 'msg': 'success', 'data': data})

    def post(self):
        summary = TokenUsageModel.get_summary()
        self.write({'code': 0, 'msg': 'success', 'data': summary})