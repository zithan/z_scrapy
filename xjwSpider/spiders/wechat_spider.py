import scrapy
from scrapy import Request

import re

from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals

from datetime import datetime
import hashlib

import urllib3

class WechatSpider(scrapy.Spider):
    name = "wechat"
    allowed_domains = ["mp.weixin.qq.com"]
    start_urls = [
        # 欧普灯饰
        # "http://weixin.sogou.com/weixin?type=1&s_from=input&query=opple4008309609",
        # 华艺灯饰照明股份
        # "http://weixin.sogou.com/weixin?type=1&s_from=input&query=huayijituan2007",
        # 艺罗兰灯饰
        "http://weixin.sogou.com/weixin?type=1&s_from=input&query=YILUOLANLIGHTING"
    ]

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="/Volumes/zithan4card/z4code/mypython/xjwSpider/tools/chromedriver")
        super(WechatSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        #当爬虫退出的时候关闭chrome
        print("spider closed")
        self.browser.quit()

    def parse(self, response):
        """
        1、根据公众号的id搜索微信公众号
        2、进入公众号获取搜狗10篇文章
        3、爬取每篇文章
        :param response:
        :return:
        """

        print('url---->' + response.url)
        print('response---->' + response.__str__())

        list_url = response.xpath('//div[@class="news-box"]/ul[@class="news-list2"]/li[1]/div[@class="gzh-box2"]/div[@class="img-box"]/a/@href').extract()
        print("list_url:" + list_url.__str__())

        try:
            yield Request(list_url[0], callback=self.parse_list)
        except Exception as e:
            pass

        pass

    def parse_list(self, response):
        print('url---->' + response.url)
        print('response---->' + response.__str__())

        # re_math = re.match(".*?('var msgList = \'{'.*'}}]}\';').*?", response.text)

        date = datetime.now().timetuple()
        dateStr = str(date.tm_year) + u'年' + str(date.tm_mon) + u'月' + str(date.tm_mday) + u'日'

        try:
            today_cards = response.xpath('//*[@id="history"]/div[1]/div[@class="weui_msg_card_hd"]/text()').extract()[0].strip()
        except Exception as e:
            today_cards = ''

        if dateStr != today_cards:
            print('今天没更新')
            return
        else:
            print('今天有更新')
            # article_title = response.xpath('/html/body/div/div[1]/div[3]/div[1]/div[2]/div/div/h4/text()').extract()[0].strip()
            # article_desc = response.xpath('/html/body/div/div[1]/div[3]/div[1]/div[2]/div/div/p[1]/text()').extract()[0].strip()
            article_path = response.xpath('/html/body/div/div[1]/div[3]/div[1]/div[2]/div/div/h4/@hrefs').extract()[0].strip()
            article_url = ["https://mp.weixin.qq.com" + article_path]

            try:
                yield Request(article_url[0], callback=self.parse_item)
            except Exception as e:
                print('访问文章异常')
                pass

        pass

    def parse_item(self, response):
        print('url---->' + response.url)
        print('response---->' + response.__str__())

        title = response.xpath('//*[@id="activity-name"]/text()').extract()[0].strip()
        brand = response.xpath('//*[@id="profileBt"]/a/text()').extract()[0].strip()
        create_time = response.xpath('//*[@id="publish_time"]/text()').extract()[0].strip()
        try:
            author = response.xpath('//*[@id="meta_content"]/p/text()').extract()[0].replace('作者', '').strip()
        except Exception as e:
            author = ''

        article_content_imgs = response.xpath('//div[@id="js_content"]//img')
        # 下载、替换微信文章中的图片
        for img in article_content_imgs:
            img_src = self.get_text(img.xpath('./@src').extract())
            img_data_src = self.get_text(img.xpath('./@data-src').extract())

            if img_data_src == None or img_data_src == '':
                img_data_src = img_src

            img_type = self.get_text(img.xpath('./@data-type').extract())
            if img_type.lower().strip() != "bmp" and img_type.lower().strip() != "jpg" and img_type.lower().strip() != "png" and img_type.lower().strip() != "jpeg":
                img_type = "jpg"

            # timestamp = self.get_time_stamp()
            img_url = hashlib.md5(img_src.encode(encoding='UTF-8')).hexdigest()
            abs_path = '/wechat/content/' + img_url + '.' + img_type
            save_path = '/images' + abs_path

            if img_data_src == None or img_data_src == '':
                continue

            img.root.attrib['src'] = abs_path
            img.root.attrib['data-src'] = abs_path

            # content = response.xpath('//div[@id="js_content"]').extract()[0]
            content = self.get_text(response.xpath('//div[@id="js_content"]').extract())

            # urllib3.urlretrieve(img_data_src.encode("utf8"), save_path)

            # 判断图片是否包含二维码，如果包含则去掉
            # 这里用python调用zbar的exe来识别二维码，因为服务器是windows 2003，装zbar插件库各种问题。
            # if self.check_qr_code(save_path):
            #     img.root.drop_tree()
            # else:
            #     img.root.attrib['src'] = abs_path
            #     img.root.attrib['data-src'] = abs_path

            # 判断图片是否包含二维码，如果包含则去掉
            # qr_code = self.get_qr_code(save_path)
            # if None != qr_code and '' != qr_code:
            #     img.root.drop_tree()
            # else :
            #     img.root.attrib['src'] = abs_path
            #     img.root.attrib['data-src'] = abs_path

        pass

    def get_text(self, texts):
        text = ""
        if len(texts) > 0:
            for tmp in texts:
                text = text + tmp
        return text.strip()
