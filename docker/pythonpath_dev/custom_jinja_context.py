import string
from superset.extensions import security_manager


# 获取当前用户信息
def get_current_user(column: string = ''):

    current_user = security_manager.current_user

    return getattr(current_user, column)
