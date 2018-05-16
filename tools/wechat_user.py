# -*- coding: utf-8 -*-
__author__ = 'zithan'

import pymysql.cursors


class WechatUser(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = pymysql.connect(host='39.108.111.29',
                             user='zithan',
                             password='Marin920',
                             db='wechat',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def get_wechat_ids(self):
        select_sql = """
            SELECT `wechat_id` FROM users
        """
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()

    def get_id(self, wechat_id):
        select_sql = """
            SELECT `id` FROM users WHERE wechat_id = '{0}'
        """.format(wechat_id)
        self.cursor.execute(select_sql)
        return self.cursor.fetchone()


if __name__ == "__main__":
    wechat_user = WechatUser()
    rs = wechat_user.get_wechat_ids()

    for item in rs:
        print(item['wechat_id'])
