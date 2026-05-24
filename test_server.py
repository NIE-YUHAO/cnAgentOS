# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import os
import sys
import traceback

# 设置标准输出编码
sys.stdout.reconfigure(encoding='utf-8')

try:
    from app.controllers.auth import LoginHandler, LogoutHandler, RegisterHandler
    from app.controllers.home import HomeHandler
    from app.controllers.admin import AdminLoginHandler, AdminIndexHandler, AdminUserHandler, AdminUserApiHandler
    
    print("OK: 成功导入控制器模块")
except Exception as e:
    print("ERROR: 导入控制器失败:", str(e))
    traceback.print_exc()
    exit(1)

class AdminLogoutHandler(tornado.web.RequestHandler):
    """管理员退出登录"""
    def get(self):
        self.clear_cookie("admin_id")
        self.redirect("/admin/login")

def make_app():
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "app", "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "app", "static"),
        "cookie_secret": "your-cookie-secret-key-change-in-production",
        "login_url": "/login",
        "xsrf_cookies": False,
        "debug": True,
    }
    return tornado.web.Application([
        (r"/", HomeHandler),
        (r"/register", RegisterHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/admin/login", AdminLoginHandler),
        (r"/admin/logout", AdminLogoutHandler),
        (r"/admin", AdminIndexHandler),
        (r"/admin/user", AdminUserHandler),
        (r"/admin/user/api", AdminUserApiHandler),
    ], **settings)

if __name__ == "__main__":
    try:
        app = make_app()
        print("OK: 成功创建应用")
        
        app.listen(10086)
        print("OK: 成功监听端口 10086")
        
        print("Server started on http://localhost:10086")
        tornado.ioloop.IOLoop.current().start()
        
    except Exception as e:
        print("ERROR: 启动服务器失败:", str(e))
        traceback.print_exc()