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


if __name__ == "__main__":
    url = 'https://mmbiz.qpic.cn/mmbiz_png/ajT9KUbORcwz828I7pWxN8XPfTiaDhStvMopGickCl41E3hiaGmW3HibnhnhSwepmoG7bpVo9j7ypTBiaW6bWd0Nagg/640?wx_fmt=png'
    down_img(url)
