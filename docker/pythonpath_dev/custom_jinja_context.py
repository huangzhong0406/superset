import string
from superset.extensions import security_manager
from datetime import datetime


# 获取当前用户信息
def get_current_user(column: string = ''):

    current_user = security_manager.current_user

    return getattr(current_user, column)


def current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def current_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
