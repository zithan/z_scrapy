# -*- coding: utf-8 -*-
__author__ = 'zithan'

import requests

# 获取代理IP的线程类
class GetIpThread():
    url = "http://dynamic.goubanjia.com/dynamic/get/"
    order = "fa78a53e3ad7e4b198ee2ae5f4831be5"
    def get_one_ip(self):
        # 获取IP
        ip = requests.get(self.url + self.order + '.html?sep=3').content.decode().strip()
        print("current ip is ------>" + ip)
        return "http://" + ip

if __name__ == '__main__':
    get_ip = GetIpThread()
    ip = get_ip.get_one_ip()
    print(ip)
