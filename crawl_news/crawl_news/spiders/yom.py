import scrapy
from crawl_news.items import CrawlNewsItem

import re
import datetime

class YomSpider(scrapy.Spider):
    name = 'yom'
    allowed_domains = ['www.yomiuri.co.jp']
    start_urls = ['https://www.yomiuri.co.jp/']

    def parse(self, response):
        '''
        トップページから最新記事のurl抽出して、各ページに飛ぶ
        '''
        for url in response.css('section.p-category-latest-sec h3 a::attr("href")').extract():
            yield scrapy.Request(url, self.parse_topics)

    def parse_topics(self, response):
        """
        各ニュースページからタイトルと本文を抜き出す。
        """
        item = CrawlNewsItem()
        item['title'] = response.css('h1 ::text').extract_first().strip() # タイトル
        body = response.css('.p-main-contents').xpath('string()').extract_first().strip() # 本文
        result = re.search('読者会員限定です', body)
        if result:
            item['body'] = None # 本文無いのでNullにしておく
        else:
            item['body'] = body
        item['source'] = self.allowed_domains[0] # 対象サイト
        item['jenre'] = None # ジャンル（後で機械学習で分類かける）
        item['date_now'] = datetime.date.today() # 抽出日
        yield item
