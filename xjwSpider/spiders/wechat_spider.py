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
        base_url + "nbdnews",
        # 艺罗兰灯饰
        # base_url + "YILUOLANLIGHTING"
        # 'https://proxy.mimvp.com/exist.php'
    ]

    # headers = {
    #     "HOST": "img01.sogoucdn.com",
    #     "Referer": "http://img01.sogoucdn.com",
    #     'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    # }

    my_save_path = "/Volumes/zithan4card/z4code/mypython/xjwSpider"

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        # get_ip = GetIpThread()
        # ip_and_port = get_ip.get_one_ip()
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

        # self.browser.find_element_by_id().get_attribute()

        super(WechatSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        #当爬虫退出的时候关闭chrome
        print("spider closed----> close chrome.....")
        self.browser.quit()

    # def start_requests(self):
    #     wechat_ids = WechatUser().get_wechat_ids()
    #     start_urls_list = []
    #     for wechat_id in wechat_ids:
    #         start_urls_list.append(self.base_url + wechat_id["wechat_id"])
    #
    #     urls = start_urls_list
    #
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

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
            today_cards = response.xpath('//*[@id="history"]/div[1]/div[@class="weui_msg_card_hd"]/text()')\
                .extract_first().strip()
        except Exception as e:
            today_cards = '时间获取异常'

        if dateStr != today_cards:
            print('今天[没]更新，今天是----->' + today_cards)
        else:
            print('今天[有]更新，今天是----->' + today_cards)

            try:
                wechat_profile = response.xpath('//p[@class="profile_account"]/text()').extract_first().strip()
                match_re = re.match(".*?([A-Za-z0-9_]+).*", wechat_profile)
                wechat_id = match_re.group(1)

                msg_card_first = response.xpath('//div[@id="history"]/div[1]/div[2]')
                # msg_card_first2 = response.xpath('/html/body/div/div[1]/div[3]/div[1]/div[2]')

                article_list = msg_card_first.xpath('./div')

                # 微信公众号一次可发多条文章
                for article in article_list:
                    title = article.xpath('.//h4[@class="weui_media_title"]/text()').extract()
                    # 因为#原创#icon
                    if len(title) == 2:
                        title = title[1].strip()
                    else:
                        title = title[0].strip()

                    desc = article.xpath('.//p[@class="weui_media_desc"]/text()').extract_first()
                    article_icon_style = article.xpath('./span[@class="weui_media_hd"]/@style').extract_first()
                    article_icon = article_icon_style[article_icon_style.find("url(") + 4:article_icon_style.find(")")]

                    current_day = "{0}_{1}_{2}".format(date.tm_year, date.tm_mon, date.tm_mday)

                    # 图片文件名
                    article_icon_name = "{0}.{1}".format(
                        hashlib.md5(article_icon.encode(encoding='UTF-8')).hexdigest(),
                        'jpg'
                    )

                    # 相对目录
                    article_icon_rel_dir = "images/{0}/{1}/article_icon".format(
                        wechat_id,
                        current_day
                    )

                    # 图片文件相对路径
                    article_icon_path = "{0}/{1}".format(article_icon_rel_dir, article_icon_name)

                    # 绝对目录
                    article_icon_abs_dir = "{0}/{1}".format(self.my_save_path, article_icon_rel_dir)
                    if not os.path.exists(article_icon_abs_dir):
                        os.makedirs(article_icon_abs_dir)

                    save_path = "{0}/{1}".format(article_icon_abs_dir, article_icon_name)
                    urlretrieve(article_icon, save_path)

                    article_path = response.xpath('.//h4[@class="weui_media_title"]/@hrefs').extract_first()

                    article_url = "https://mp.weixin.qq.com{0}".format(article_path)

                    wechat_id_and_title = wechat_id + title
                    article_hash_id = hashlib.md5(wechat_id_and_title.encode(encoding="UTF-8")).hexdigest()

                    meta = {
                        "article_hash_id": article_hash_id,
                        "title": title,
                        "desc": desc,
                        "article_icon_path": article_icon_path
                    }

                    yield Request(article_url, meta=meta, callback=self.parse_item)

            except Exception as e:
                print(e)

    def parse_item(self, response):
        print('wechat item url---->' + response.url)
        print('wechat item response---->' + response.__str__())

        article_hash_id = response.meta.get("article_hash_id", "")
        title = response.meta.get("title", "")
        desc = response.meta.get("desc", "")
        article_icon_path = response.meta.get("article_icon_path", "")

        try:
            # var ct = "1526451420";
            text = response.text
            pulish_time = text[text.find('var ct = "')+10:text.find('var publish_time')].strip()
            pulish_time = int(pulish_time.rstrip('";'))

            pass
            author = response.xpath('//*[@id="meta_content"]/p/text()').extract()[0].replace('作者', '').strip()

        except Exception as e:
            print(e)

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


        # article_item["id"] = hashlib.md5(response.url.encode(encoding='UTF-8')).hexdigest()
        # article_item["title"] = title
        # article_item["brand"] = brand
        # article_item["create_time"] = create_time
        # article_item["author"] = author
        # article_item["content"] = content
        # article_item["wechat_image_urls"] = [brand_avatar]

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
