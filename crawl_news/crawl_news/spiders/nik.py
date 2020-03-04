import scrapy
from crawl_news.items import CrawlNewsItem

import re
import datetime

class NikSpider(scrapy.Spider):
    name = 'nik'
    allowed_domains = ['www.nikkei.com']
    start_urls = ['https://www.nikkei.com/']

    def parse(self, response):
        '''
        トップニュースのurl取得

        '''
        url_list = response.css('.k-hub-layout__container--headline.k-hub-layout__container a::attr("href")').re(r'/article/.*')
        uniq_url = set(url_list) # urlが重複で取得されているので、重複削除
        for url in uniq_url:
            yield scrapy.Request(response.urljoin(url), self.parse_topics) # 相対urlなのでurljoin使う

    def parse_topics(self, response):
        """
        各ニュースページからタイトルと本文を抜き出す。
        """
        item = CrawlNewsItem()
        item['title'] = ','.join(response.css('h1 ::text').extract()).strip() # タイトル
        item['body'] = response.css('.main-text').xpath('string()').extract_first().strip() # 本文
        item['source'] = self.allowed_domains[0] # 対象サイト
        item['jenre'] = None # ジャンル（後で機械学習で分類かける）
        item['date_now'] = datetime.date.today() # 抽出日
        yield item