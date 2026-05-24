import tornado.ioloop
import tornado.web
import os

from app.controllers.auth import LoginHandler, LogoutHandler, RegisterHandler
from app.controllers.home import HomeHandler
from app.controllers.admin import (
    AdminLoginHandler, AdminIndexHandler, AdminLogoutHandler,
    AdminUserHandler, AdminUserApiHandler,
    AdminFunctionHandler, AdminFunctionApiHandler,
    AdminRoleHandler, AdminRoleApiHandler,
    AdminPermissionHandler, AdminPermissionApiHandler,
    AdminObservationSourceHandler, AdminObservationSourceApiHandler,
    AdminApiInterfaceHandler, AdminApiInterfaceApiHandler,
    AdminDigitalWorkerHandler, AdminDigitalWorkerApiHandler
)
from app.controllers.model import (
    AdminModelHandler, AdminModelApiHandler, AdminModelSetDefaultHandler,
    AdminModelTestHandler, AdminModelTestApiHandler, AdminModelStreamHandler,
    AdminTokenStatsHandler, AdminTokenStatsApiHandler
)

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

        (r"/admin/function", AdminFunctionHandler),
        (r"/admin/function/api", AdminFunctionApiHandler),

        (r"/admin/role", AdminRoleHandler),
        (r"/admin/role/api", AdminRoleApiHandler),

        (r"/admin/permission", AdminPermissionHandler),
        (r"/admin/permission/api", AdminPermissionApiHandler),

        (r"/admin/observation", AdminObservationSourceHandler),
        (r"/admin/observation/api", AdminObservationSourceApiHandler),

        (r"/admin/api_interface", AdminApiInterfaceHandler),
        (r"/admin/api_interface/api", AdminApiInterfaceApiHandler),

        (r"/admin/digital_worker", AdminDigitalWorkerHandler),
        (r"/admin/digital_worker/api", AdminDigitalWorkerApiHandler),

        (r"/admin/model", AdminModelHandler),
        (r"/admin/model/api", AdminModelApiHandler),
        (r"/admin/model/set_default", AdminModelSetDefaultHandler),
        (r"/admin/model/test", AdminModelTestHandler),
        (r"/admin/model/test/api", AdminModelTestApiHandler),
        (r"/admin/model/stream", AdminModelStreamHandler),
        (r"/admin/token/stats", AdminTokenStatsHandler),
        (r"/admin/token/stats/api", AdminTokenStatsApiHandler),
    ], **settings)

if __name__ == "__main__":
    app = make_app()
    app.listen(10086)
    print("Server started on http://localhost:10086")
    tornado.ioloop.IOLoop.current().start()