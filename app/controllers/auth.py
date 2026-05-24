import tornado.web
import bcrypt
from app.controllers.base import BaseHandler
from app.models.user import UserModel

class RegisterHandler(BaseHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        username = self.get_argument("username", "").strip()
        password = self.get_argument("password", "").strip()
        confirm = self.get_argument("confirm_password", "").strip()

        if not username or not password:
            self.write("用户名和密码不能为空")
            return
        if password != confirm:
            self.write("两次输入的密码不一致")
            return
        if UserModel.get_by_username(username):
            self.write("用户名已存在")
            return

        # 哈希密码
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_id = UserModel.create(username, hashed.decode('utf-8'))
        if user_id:
            self.set_secure_cookie("user_id", str(user_id))
            self.redirect("/")
        else:
            self.write("注册失败，请重试")

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.get_argument("username", "").strip()
        password = self.get_argument("password", "").strip()

        user = UserModel.get_by_username(username)
        if not user:
            self.write("用户名或密码错误")
            return

        # 验证密码
        stored_hash = user['password_hash'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            self.set_secure_cookie("user_id", str(user['id']))
            self.redirect("/")
        else:
            self.write("用户名或密码错误")

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user_id")
        self.redirect("/login")