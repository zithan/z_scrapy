# -*- coding: utf-8 -*-
__author__ = 'zithan'

import requests


class GetIpThread(object):
    # 获取代理IP的线程类

    def judge_ip(self, ip_and_port):
        #判断ip是否可用
        http_url = "https://www.baidu.com"
        proxy_url = "http://{0}".format(ip_and_port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("valid ip and port --------- {0}".format(proxy_url))
                return True
            else:
                print("--------- invalid ip and port ---------{0}".format(proxy_url))
                return False

    def get_one_ip(self):
        # 获取IP
        url = "http://dynamic.goubanjia.com/dynamic/get/"
        order = "fa78a53e3ad7e4b198ee2ae5f4831be5"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"}

        ip_and_port = requests.get(url + order + '.html?sep=3', headers=headers).content.decode().strip()

        judge_re = self.judge_ip(ip_and_port)
        if judge_re:
            return "http://{0}".format(ip_and_port)
        # else:
            # return self.get_one_ip()


if __name__ == '__main__':
    get_ip = GetIpThread()
    ip = get_ip.get_one_ip()
    print(ip)
