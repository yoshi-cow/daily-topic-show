# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlNewsItem(scrapy.Item):
    '''
    スクレイピングデータ保存用クラス
    '''

    title = scrapy.Field()  # ニュースタイトル
    body = scrapy.Field()   # 本文
    source = scrapy.Field() # サイトドメイン
    jenre = scrapy.Field()  # ニュースジャンル（後で機械学習で設定）
    date_now = scrapy.Field()   # 取得日