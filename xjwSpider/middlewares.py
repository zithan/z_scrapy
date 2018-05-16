# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

from fake_useragent import UserAgent
from tools.get_proxy_ip import GetIpThread

from scrapy.http import HtmlResponse
import time
from scrapy import signals


class XjwspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class XjwspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddlware(object):
    #随机更换user-agent
    def __init__(self, crawler):
        super(RandomUserAgentMiddlware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        print("-------User-Agent------{0}".format(get_ua()))
        request.headers.setdefault('User-Agent', get_ua())
        # request.meta["proxy"] = "https://106.111.45.183:61234"


class RandomProxyMiddleware(object):
    # 动态设置ip代理

    def process_request(self, request, spider):
        get_ip = GetIpThread()
        ip_and_port = get_ip.get_one_ip()
        request.meta["proxy"] = ip_and_port


class JSPageMiddleware(object):
    # 通过chrome请求动态网页

    def process_request(self, request, spider):
        import re
        if spider.name == "wechat":

            spider.browser.get(request.url)
            print("chromedriver-访问---------->:{0}".format(request.url))
            time.sleep(5)

            try:
                is_match_sogou = re.match('http://weixin.sogou.com/antispider', request.url.strip())
                if is_match_sogou:
                    seccode_img_element = spider.browser.find_element_by_id('seccodeImage')
                    if seccode_img_element:
                        print('发现搜狗验证码...尼玛...开始解码...')

                        # 截图
                        spider.browser.get_screenshot_as_file('wescreenshot_sg.png')

                        left = int(seccode_img_element.location['x'])
                        top = int(seccode_img_element.location['y'])
                        right = int(seccode_img_element.location['x'] + seccode_img_element.size['width'])
                        bottom = int(seccode_img_element.location['y'] + seccode_img_element.size['height'])

                        from PIL import Image
                        # 通过Image处理图像
                        im = Image.open('wescreenshot_sg.png')
                        im = im.crop((left, top, right, bottom))
                        # 保存验证码图片
                        im.save('seccode.png')

                        # im = open('seccode.jpg', 'rb').read()
                        from tools.yundama import get_captcha_code
                        code = get_captcha_code('seccode.png', 1006)
                        print("搜狗验证码是------>{0}".format(code))

                        # 模拟输入验证码，并提交
                        elem = spider.browser.find_element_by_id("seccodeInput")
                        elem.clear()
                        elem.send_keys(code)
                        spider.browser.find_element_by_id("submit").click()

                        # 延时5秒，等待完成页面跳转
                        time.sleep(3)

            except Exception as e:
                print(e)

            try:
                is_match_wechat = re.match('http://mp.weixin.qq.com/profile', request.url.strip())
                if is_match_wechat:
                    verify_img_element = spider.browser.find_element_by_id('verify_img')
                    if verify_img_element:
                        print('发现微信验证码...尼玛...开始解码...')

                        # 截图
                        spider.browser.get_screenshot_as_file('wescreenshot_wx.png')

                        left = int(verify_img_element.location['x'])
                        top = int(verify_img_element.location['y'])
                        right = int(verify_img_element.location['x'] + verify_img_element.size['width'])
                        bottom = int(verify_img_element.location['y'] + verify_img_element.size['height'])

                        from PIL import Image
                        # 通过Image处理图像
                        im = Image.open('wescreenshot_wx.png')
                        im = im.crop((left, top, right, bottom))
                        # 保存验证码图片
                        im.save('verifycode.png')

                        # im = open('verifycode.png', 'rb').read()
                        from tools.yundama import get_captcha_code
                        code = get_captcha_code('verifycode.png')
                        print("微信验证码是------>{0}".format(code))

                        # 模拟输入验证码，并提交
                        elem = spider.browser.find_element_by_id("input")
                        elem.clear()
                        elem.send_keys(code)
                        spider.browser.find_element_by_id("bt").click()

                        # 延时5秒，等待完成页面跳转
                        time.sleep(3)

            except Exception as e:
                print(e)

            # 等待加载完成
            time.sleep(3)

            return HtmlResponse(
                url=spider.browser.current_url,
                body=spider.browser.page_source,
                encoding="utf-8",
                request=request)
