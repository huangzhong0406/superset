import string
import os
from superset.extensions import security_manager
from datetime import datetime
import pandas as pd
import MySQLdb
from MySQLdb import cursors


# 获取当前用户信息
def get_current_user(column: string = ''):
    current_user = security_manager.current_user

    return getattr(current_user, column)


def current_date():
    return datetime.now().strftime('%Y-%m-%d')


def current_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def getTopLevelCompanyUuid():
    return '14748906195710318'


# 连接singoo_pms数据库
def get_singoopms_data(sql: string = '', is_more: bool = False):
    # host = os.getenv("DB_HOST_SINGOOPMS")
    # port = os.getenv("DB_PORT_SINGOOPMS")
    # database = os.getenv("DB_DATABASE_SINGOOPMS")
    # user = os.getenv("DB_USERNAME_SINGOOPMS")
    # password = os.getenv("DB_PASSWORD_SINGOOPMS")

    host = os.environ.get("DB_HOST_SINGOOPMS")
    port = os.environ.get("DB_PORT_SINGOOPMS")
    database = os.environ.get("DB_DATABASE_SINGOOPMS")
    user = os.environ.get("DB_USERNAME_SINGOOPMS")
    password = os.environ.get("DB_PASSWORD_SINGOOPMS")

    db = MySQLdb.connect(host=host, port=port, user=user, password=password,
                         database=database, cursorclass=cursors.DictCursor,
                         charset="utf8")

    cursor = db.cursor()
    cursor.execute(sql)

    if is_more:
        data = cursor.fetchall()
    else:
        data = cursor.fetchone()

    cursor.close()

    return data


# contract_performance 数据集权限
def contract_performance_data_permission():
    current_user_id = get_current_user('oa_user_id')
    current_uid = get_current_user('oa_uid')
    current_cid = get_current_user('oa_cid')

    # 管理员
    if current_user_id == 1:
        return '1=1'

    # 公司老板
    company = get_singoopms_data(
        "select * from iam_companies WHERE uuid = '%s' AND user_id = %s"
        % (current_cid, current_user_id))
    if company is not None:
        # 返回sql 条件语句
        return 'company_id = ' + '\'' + company['uuid'] + '\''

    support_companies = get_singoopms_data(
        "SELECT com.id, com.uuid, com.name, com_sp.user_id, com_sp.support_position FROM iam_company_support_personnels com_sp LEFT JOIN iam_companies com ON com.id = com_sp.company_id WHERE com_sp.user_id =  %s"
        % current_user_id, True)

    support_companies = pd.DataFrame(support_companies)

    # 渠道商管理权限
    if support_companies.size > 0:

        if current_cid == getTopLevelCompanyUuid():
            company_uuids = support_companies['uuid'].tolist()
            company_uuids = "','".join(company_uuids)

            # 返回sql 条件语句
            return "company_id in (\'" + company_uuids + "\')"

    # 部门主管权限
    managedTeams = get_singoopms_data("SELECT * FROM iam_teams WHERE team_master = %s"
                                      % current_user_id, True)
    managedTeams = pd.DataFrame(managedTeams)
    if managedTeams.size > 0:
        team_uuids = managedTeams['uuid'].tolist()
        team_uuids = "','".join(team_uuids)

        return "team_id in (\'" + team_uuids + "\')"

    # 自己看自己
    return 'user_id = \'%s\'' % current_uid
