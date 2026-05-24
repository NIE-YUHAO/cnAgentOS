import tornado.web
from app.models.user import UserModel

class BaseHandler(tornado.web.RequestHandler):
    """提供统一的当前用户获取逻辑"""

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id:
            return None
        # user_id 是 bytes，转换为 int
        user_id = int(user_id.decode('utf-8'))
        return UserModel.get_by_id(user_id)

    def get_current_user_name(self):
        user = self.get_current_user()
        return user['username'] if user else None