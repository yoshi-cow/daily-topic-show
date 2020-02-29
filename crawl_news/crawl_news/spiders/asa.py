from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from crawl_news.items import CrawlNewsItem

import datetime
import re

class AsaSpider(CrawlSpider):
    name = 'asa'
    allowed_domains = ['www.asahi.com']
    start_urls = ['https://www.asahi.com/']

    # 主要ニュースのurl取得
    rules = (
        Rule(LinkExtractor(allow=r'\.html\?iref=comtop_8_0\d$'), callback='parse_topics'),
    )

    def parse_topics(self, response):
        """
        各ニュースページからタイトルと本文を抜き出す。
        """
        item = CrawlNewsItem()
        item['title'] = response.css('.Title h1 ::text').extract_first().strip() # タイトル
        item['body'] = response.css('.ArticleText').xpath('string()').extract_first().strip() # 本文
        item['source'] = self.allowed_domains[0] # 対象サイト
        item['jenre'] = None # ジャンル（後で機械学習で分類かける）
        item['date_now'] = datetime.date.today() # 抽出日
        yield item