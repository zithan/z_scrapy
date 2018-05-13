import scrapy
from scrapy import Request

from datetime import datetime

class WechatSpider(scrapy.Spider):
    name = "wechat"
    allowed_domains = ["weixin.sogou.com", "mp.weixin.qq.com"]
    start_urls = [
        # 欧普灯饰
        # "http://weixin.sogou.com/weixin?type=1&s_from=input&query=opple4008309609",
        # 华艺灯饰照明股份
        # "http://weixin.sogou.com/weixin?type=1&s_from=input&query=huayijituan2007",
        # 艺罗兰灯饰
        "http://weixin.sogou.com/weixin?type=1&s_from=input&query=YILUOLANLIGHTING"
    ]

    # allowed_domains = ["mp.weixin.qq.com"]
    # start_urls = ["https://mp.weixin.qq.com/s?timestamp=1526214047&src=3&ver=1&signature=UoKxE4Y4kCDHaAgVk4yVezIF1CZ6dh0wi*wmimG8c-17LB96WlHkWrhVOP4AulUU8B9WbNhjcZN0guI5kVK8sfBi*ew2S3AgCjvwBV3T31Gnw6ZI1qElsSZ3-gg8INlEak7b86A6-HJLiQeUmVYaa2yHsMIfDCCATJjgFuEsXUM="]

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


        # title = response.xpath('//*[@id="activity-name"]/text()').extract()[0].strip()
        # brand = response.xpath('//*[@id="profileBt"]/a/text()').extract()[0].strip()
        # create_time = response.xpath('//*[@id="publish_time"]/text()').extract()[0].strip()
        # try:
        #     author = response.xpath('//*[@id="meta_content"]/p/text()').extract()[0].replace('作者', '').strip()
        # except Exception as e:
        #     author = ''
        # content = response.xpath('//div[@id="js_content"]').extract()[0]
        # rs = response.xpath('//*[@id="activity-name"]/text()').extract()[0].strip()
        # # rs = response.xpath('//*[@id="post-113909"]/div[1]/h1/text()').extract()[0].strip()
        # print(rs)

        pass

    def parse_list(self, response):
        print('url---->' + response.url)
        print('response---->' + response.__str__())

        date = datetime.now().timetuple()
        dateStr = str(date.tm_year) + u'年' + str(date.tm_mon) + u'月' + str(date.tm_mday) + u'日'

        today_cards = response.xpath('//*[@id="history"]/div[1]/div[@class="weui_msg_card_hd"]/text()').extract()

        pass
