import scrapy
import os
from scrapy import Request

from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals

from xjwSpider.items import WechatArticleItem

from datetime import datetime
import hashlib
import re

from urllib.request import urlretrieve
from urllib import parse

from tools.get_proxy_ip import GetIpThread

import time

from tools.wechat_user import WechatUser

class WechatSpider(scrapy.Spider):
    name = "wechat"
    base_url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='
    allowed_domains = ["weixin.sogou.com", "mp.weixin.qq.com"]
    start_urls = [
        # 亚太灯饰传媒
        # base_url + "aluoyidi888",
        # 每日经济新闻
        # base_url + "nbdnews",
        # 艺罗兰灯饰
        # base_url + "YILUOLANLIGHTING"
        # 'https://proxy.mimvp.com/exist.php'
    ]

    # headers = {
    #     "HOST": "img01.sogoucdn.com",
    #     "Referer": "http://img01.sogoucdn.com",
    #     'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    # }

    def __init__(self):
        wechat_ids = WechatUser().get_wechat_ids()
        start_urls_list = []
        for wechat_id in wechat_ids:
            start_urls_list.append(self.base_url + wechat_id["wechat_id"])

        self.start_urls = start_urls_list

        get_ip = GetIpThread()
        ip_and_port = get_ip.get_one_ip()
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--proxy-server={0}'.format(ip_and_port))

        # prefs = {
        #     'profile.default_content_setting_values': {
        #         'images': 2
        #     }
        # }
        # chrome_options.add_experimental_option('prefs', prefs)

        self.browser = webdriver.Chrome(
            executable_path="/Volumes/zithan4card/z4code/mypython/xjwSpider/tools/chromedriver",
            chrome_options=chrome_options
        )
        super(WechatSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        #当爬虫退出的时候关闭chrome
        print("spider closed----> close chrome.....")
        self.browser.quit()

    def parse(self, response):
        """
        1、根据公众号的id搜索微信公众号，取第一个
        2、进入公众号获取搜狗10篇文章
        3、爬取当天文章
        :param response:
        :return:
        """

        print('sogou url---->' + response.url)
        print('sogou response---->' + response.__str__())

        # 判断搜狗是否出现验证码
        if re.match('http://weixin.sogou.com/antispider', response.url):
            print('搜狗出现验证码2')
            return

        # try:
        #     proxy_ip = response.xpath('//*[@id="mimvp-body"]/div[1]/div[1]/span[2]/font[1]/text()').extract()[0].strip()
        #     print('当前代理ip为{0}'.format(proxy_ip))
        #     return
        # except Exception as e:
        #     print('查看代理...异常')


        list_url = response.xpath('//div[@class="news-box"]/ul[@class="news-list2"]/li[1]/div[@class="gzh-box2"]/div[@class="img-box"]/a/@href').extract()
        print("wechat office url on sogou---->:" + list_url.__str__())

        try:
            print("---------ready to wechat -----------")
            yield Request(list_url[0], callback=self.parse_list)
        except Exception as e:
            print("---获取微信公众号路径异常---")

        # 提取下一个并交给scrapy进行下载
        # next_urls = ["aluoyidi888", "gh_0f86876af6ce", "opplezm"]
        #
        # for next_url in next_urls:
        #     print('----next office is [{0}]-------'.format(next_url))
        #     yield Request(url=self.base_url + next_url, callback=self.parse)

    def parse_list(self, response):
        print('[wechat list] url---->' + response.url)
        print('[wechat list] response---->' + response.__str__())

        # re_math = re.match(".*?('var msgList = \'{'.*'}}]}\';').*?", response.text)

        date = datetime.now().timetuple()
        dateStr = str(date.tm_year) + u'年' + str(date.tm_mon) + u'月' + str(date.tm_mday) + u'日'

        try:
            today_cards = response.xpath('//*[@id="history"]/div[1]/div[@class="weui_msg_card_hd"]/text()').extract()[0].strip()
        except Exception as e:
            today_cards = '时间获取异常'

        if dateStr != today_cards:
            print('今天[没]更新，今天是----->' + today_cards)
        else:
            print('今天[有]更新，今天是----->' + today_cards)
            # article_title = response.xpath('/html/body/div/div[1]/div[3]/div[1]/div[2]/div/div/h4/text()').extract()[0].strip()
            # article_desc = response.xpath('/html/body/div/div[1]/div[3]/div[1]/div[2]/div/div/p[1]/text()').extract()[0].strip()

            try:
                brand_title = response.xpath('/html/body/div[1]/div[1]/div[1]/div[1]/div/strong/text()').extract()[0].strip()
                article_title = response.xpath('//*[@id="WXAPPMSG1000000082"]/div/h4/text()').extract()[0].strip()
                article_path = response.xpath('/html/body/div/div[1]/div[3]/div[1]/div[2]/div/div/h4/@hrefs').extract()[0].strip()
                article_url = ["https://mp.weixin.qq.com" + article_path]
                brand_avatar = response.xpath('/html/body/div[1]/div[1]/div[1]/div[1]/span/img/@src').extract()[0].strip()

                yield Request(article_url[0], meta={"brand_avatar": brand_avatar}, callback=self.parse_item)
            except Exception as e:
                print('访问文章异常')

    def parse_item(self, response):
        # todo captcha
        print('wechat item url---->' + response.url)
        print('wechat item response---->' + response.__str__())

        brand_avatar = response.meta.get("brand_avatar", "")
        title = response.xpath('//*[@id="activity-name"]/text()').extract()[0].strip()
        brand = response.xpath('//*[@id="profileBt"]/a/text()').extract()[0].strip()
        create_time = response.xpath('//*[@id="publish_time"]/text()').extract()[0].strip()
        try:
            author = response.xpath('//*[@id="meta_content"]/p/text()').extract()[0].replace('作者', '').strip()
        except Exception as e:
            author = '无'

        article_content_imgs = response.xpath('//div[@id="js_content"]//img')
        # 下载、替换微信文章中的图片
        for img in article_content_imgs:
            img_src = self.get_text(img.xpath('./@src').extract())
            img_data_src = self.get_text(img.xpath('./@data-src').extract())

            if img_data_src == None or img_data_src == '':
                img_data_src = img_src

            img_type = self.get_text(img.xpath('./@data-type').extract())
            if img_type.lower().strip() != "bmp" and img_type.lower().strip() != "jpg" \
                    and img_type.lower().strip() != "png" and img_type.lower().strip() != "jpeg":
                img_type = "jpg"

            img_name = hashlib.md5(img_data_src.encode(encoding='UTF-8')).hexdigest()
            abs_path = img_name + '.' + img_type
            save_path = "/Volumes/zithan4card/z4code/mypython/xjwSpider/xjwSpider/spiders/images/" + abs_path

            # if img_data_src == None or img_data_src == '':
            #     continue

            # print('img_data_src---->' + img_data_src);
            urlretrieve(img_data_src, save_path)

            img.root.attrib['src'] = abs_path
            img.root.attrib['data-src'] = abs_path

        # content = response.xpath('//div[@id="js_content"]').extract()[0]
        content = self.get_text(response.xpath('//div[@id="js_content"]').extract())

        article_item = WechatArticleItem()


        article_item["id"] = hashlib.md5(response.url.encode(encoding='UTF-8')).hexdigest()
        article_item["title"] = title
        article_item["brand"] = brand
        article_item["create_time"] = create_time
        article_item["author"] = author
        article_item["content"] = content
        article_item["wechat_image_urls"] = [brand_avatar]

        yield article_item


    def upload_content_image(self, response):
        with open(response.meta.get("save_path"), "wb") as f:
            f.write(response.body)
            f.close()

    def get_text(self, texts):
        text = ""
        if len(texts) > 0:
            for tmp in texts:
                text = text + tmp
        return text.strip()
