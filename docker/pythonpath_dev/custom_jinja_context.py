import string
import os
from superset.extensions import security_manager
from datetime import datetime
from dateutil.relativedelta import relativedelta
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


def min_start_time(start, end):
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')
    want_days = (end - start).days
    modified_date = start + relativedelta(days=-1 * want_days)
    modified_date2 = start + relativedelta(years=-1)
    res = modified_date2
    if (modified_date - modified_date2).days < 0:
        res = modified_date
    res = res.strftime("%Y-%m-%d")
    return res


def getTopLevelCompanyUuid():
    return '14748906195710318'


def get_singoopms_data(sql: string = '', is_more: bool = False):
    """
    连接singoo_pms数据库
    :param string sql:
    :param bool is_more:
    :return
    """
    # host = os.getenv("DB_HOST_SINGOOPMS")
    # port = os.getenv("DB_PORT_SINGOOPMS")
    # database = os.getenv("DB_DATABASE_SINGOOPMS")
    # user = os.getenv("DB_USERNAME_SINGOOPMS")
    # password = os.getenv("DB_PASSWORD_SINGOOPMS")

    host = os.environ.get("DB_HOST_SINGOOPMS")
    port = int(os.environ.get("DB_PORT_SINGOOPMS"))
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


def contract_performance_data_permission(alias: string = '') -> str:
    """
    contract_performance 数据集权限
    contract_performance_data_permission

    :param str alias: contract_performances table alias
    :return: string
    """
    current_user_id = get_current_user('oa_user_id')
    current_uid = get_current_user('oa_uid')
    current_cid = get_current_user('oa_cid')

    # contract_performances表别名
    if alias:
        alias = alias + '.'

    # 管理员
    if current_user_id == 1:
        return '1=1'

    # 公司老板
    company = get_singoopms_data(
        "select * from iam_companies WHERE uuid = '%s' AND user_id = %s"
        % (current_cid, current_user_id))
    if company is not None:
        # 返回sql 条件语句
        return alias + 'company_id = ' + '\'' + company['uuid'] + '\''

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
            return alias + "company_id in (\'" + company_uuids + "\')"

    # 部门主管权限
    managedTeams = get_singoopms_data("SELECT * FROM iam_teams WHERE team_master = %s"
                                      % current_user_id, True)
    managedTeams = pd.DataFrame(managedTeams)
    if managedTeams.size > 0:
        team_uuids = managedTeams['uuid'].tolist()
        team_uuids = "','".join(team_uuids)

        return alias + "team_id in (\'" + team_uuids + "\')"

    # 自己看自己
    return alias + 'user_id = \'%s\'' % current_uid
