import scrapy
from crawl_news.items import CrawlNewsItem

import re
import datetime

class MaiSpider(scrapy.Spider):
    name = 'mai'
    allowed_domains = ['mainichi.jp']
    start_urls = ['https://mainichi.jp/']

    def parse(self, response):
        '''
        トップニュースのurl取得
        '''
        for url in response.css('.main-box a::attr("href")').re(r'.*/articles/.*'):
                yield scrapy.Request(response.urljoin(url), self.parse_topics) # 相対urlなのでurljoin使う

    def parse_topics(self, response):
        """
        各ニュースページからタイトルと本文を抜き出す。
        """
        item = CrawlNewsItem()
        item['title'] = response.css('h1 ::text').extract_first().strip() # タイトル
        item['body'] = response.css('.main-text').xpath('string()').extract_first().strip() # 本文
        item['source'] = self.allowed_domains[0] # 対象サイト
        item['jenre'] = None # ジャンル（後で機械学習で分類かける）
        item['date_now'] = datetime.date.today() # 抽出日
        yield item