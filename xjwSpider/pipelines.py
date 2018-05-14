# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql.cursors

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem


class XjwspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipelin(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = pymysql.connect(host='39.108.111.29',
                             user='zithan',
                             password='Marin920',
                             db='wechat',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article2(title, brand, author, content, create_time)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["brand"], item["author"], item["content"], item["create_time"]))
        self.conn.commit()


class ArticleImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['wechat_image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        brand_avatar = [x['path'] for ok, x in results if ok]  # ok判断是否下载成功
        if not brand_avatar:
            raise DropItem("Item contains no images")
        item['brand_avatar'] = brand_avatar
        return item
