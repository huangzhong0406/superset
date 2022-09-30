
from flask import redirect, g, flash, request
from flask_appbuilder.security.views import UserDBModelView, AuthDBView
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.views import expose
from flask_appbuilder.security.manager import BaseSecurityManager
from flask_login import login_user, logout_user


class CustomAuthDBView(AuthDBView):

    @expose('/login2/', methods=['GET', 'POST'])
    def login(self):
        redirect_url = self.appbuilder.get_url_for_index
        user_name = request.args.get('username')
        password = request.args.get('password')
        user_role = request.args.get('role')
        user_id = request.args.get('id')
        if user_name is not None:
            user = self.appbuilder.sm.find_user(username=user_name)
            if not user:
                role = self.appbuilder.sm.find_role(user_role)
                user = self.appbuilder.sm.add_user(user_name, user_name, 'last_name',
                                                   user_name + "@singoo.cc", role,
                                                   password=password)
            if user:
                login_user(user, remember=False)
                return redirect(redirect_url)

        else:
            print('Unable to auto login', 'warning')
            return super(CustomAuthDBView, self).login()


class CustomSecurityManager(SupersetSecurityManager):
    authdbview = CustomAuthDBView

    def __init__(self, appbuilder):
        super(CustomSecurityManager, self).__init__(appbuilder)
