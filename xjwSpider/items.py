# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime

from scrapy.loader.processors import MapCompose, TakeFirst, Join


class XjwspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def return_value(value):
    return value


class WechatArticleItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    create_time = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    wechat_image_urls = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    brand_avatar = scrapy.Field()
