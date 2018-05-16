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


class WechatArticleItem(scrapy.Item):
    article_hash_id = scrapy.Field()
    user_id = scrapy.Field()
    title = scrapy.Field()
    desc = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    article_icon_path = scrapy.Field()
