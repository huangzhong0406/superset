
from flask import redirect, g, flash, request
from flask_appbuilder.security.views import UserDBModelView, AuthDBView
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.views import expose
from flask_appbuilder.security.manager import BaseSecurityManager
from flask_login import login_user, logout_user
from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, String, Integer
from superset.extensions import security_manager


class CustomAuthDBView(AuthDBView):

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):

        # 先退出已登录用户
        if security_manager.current_user is not None:
            logout_user()

        redirect_url = self.appbuilder.get_url_for_index
        user_name = request.args.get('username')
        email = request.args.get('email')
        password = request.args.get('password')
        user_role = request.args.get('role')
        oa_user_id = request.args.get('id')
        oa_uid = request.args.get('oa_uid')
        oa_cid = request.args.get('oa_cid')

        if user_name is not None:
            user = self.appbuilder.sm.find_user(username=user_name)
            if not user:

                # 邮箱重复返回登录页
                if self.appbuilder.sm.find_user(email=email) is not None:
                    return super(CustomAuthDBView, self).login()

                role = self.appbuilder.sm.find_role(user_role)
                user = self.appbuilder.sm.add_user(
                    user_name,
                    user_name,
                    '',
                    email,
                    role,
                    password=password
                )

                user.oa_user_id = oa_user_id
                user.oa_uid = oa_uid
                user.oa_cid = oa_cid

                self.appbuilder.sm.update_user(user)

            if user:
                login_user(user, remember=False)
                return redirect(redirect_url)

        else:
            print('Unable to auto login', 'warning')
            return super(CustomAuthDBView, self).login()


class CustomUser(User):
    __tablename__ = "ab_user"

    oa_user_id = Column(Integer)
    oa_uid = Column(String(36))
    oa_cid = Column(String(36))


class CustomSecurityManager(SupersetSecurityManager):
    user_model = CustomUser
    authdbview = CustomAuthDBView

    def __init__(self, appbuilder):
        super(CustomSecurityManager, self).__init__(appbuilder)
