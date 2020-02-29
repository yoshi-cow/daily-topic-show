import scrapy
from crawl_news.items import CrawlNewsItem

import re
import datetime

class SanSpider(scrapy.Spider):
    name = 'san'
    allowed_domains = ['www.sankei.com']
    start_urls = ['https://www.sankei.com/']

    def parse(self, response):
        '''
        トップページの主要６記事のurlを取得
        '''
        i = 1
        for url in response.css('div.column_center section h3.entry_title a::attr("href")').re(r'.*/news/.*\.html'):
            yield scrapy.Request(response.urljoin(url), self.parse_topics) # 相対urlなのでurljoin使う
            if i == 6:
                break
            i += 1

    def parse_topics(self, response):
        """
        各ニュースページからタイトルと本文を抜き出す。
        """
        item = CrawlNewsItem()
        item['title'] = response.css('#__r_article_title__ ::text').extract_first().strip() # タイトル
        item['body'] = response.css('.post_content').xpath('string()').extract_first().strip() # 本文
        item['source'] = self.allowed_domains[0] # 対象サイト
        item['jenre'] = None # ジャンル（後で機械学習で分類かける）
        item['date_now'] = datetime.date.today() # 抽出日
        yield item
        # pass