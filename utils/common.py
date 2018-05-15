# -*- coding: utf-8 -*-
__author__ = 'zithan'

import hashlib
import scrapy
from urllib.request import urlretrieve


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def down_img(url2):
    # response = scrapy.Request(url2)
    # with open("./images/captcha.jpg", "wb") as f:
    #     f.write(response.body)
    #     f.close()

    urlretrieve(url2, "./images/captcha.jpg")


def is_detail_url(url):
    import re
    return re.match('https://mp.weixin.qq.com/profile', url)


if __name__ == "__main__":
    url = 'http://mp.weixin.qq.com/profile?src=3&timestamp=1526356751&ver=1&signature=xTwF1KNdk5Fq3u4BQOKWZgkyz-8-nbeUeQfP670*w7G6RGDjtbs7SteH16BjpB*tuucD2asgJol1XGjhGSJ17g=='
    # down_img(url)
    print(is_detail_url(url))
