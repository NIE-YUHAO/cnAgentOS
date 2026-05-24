from app.controllers.base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect("/login")
            return
        self.render("index.html", username=user['username'])