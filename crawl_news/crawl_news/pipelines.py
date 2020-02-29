# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.exceptions import DropItem

import MySQLdb

class ValidationPipeline(object):
    """
    Item検証用Pipeline
    """
    def process_item(self, item, spider):
        if not item['title']:
            # title未取得時はitemを廃棄する
            raise DropItem('No title')

        if not item['body']:
            # 本文が無い時は、Null値を入れる
            item['body'] = None
        
        return item


class MySQLPipeline(object):
    '''
    抽出データitem保存用Pipeline
    '''
    def open_spider(self, spider):
        '''
        Spider開始時にローカルのMySQLサーバーに接続
        '''
        settings = spider.settings
        params = {
            'host': settings.get('MYSQL_HOST', '127.0.0.1'),
            'db': settings.get('MYSQL_DATABASE', 'news_db'),
            'user': settings.get('MYSQL_USER', 'news_scraper'),
            'passwd': settings.get('MySQL_PASSWORD', 'password'),
            'charset': settings.get('MYSQL_CHARSET', 'utf8mb4'),
        }
        self.conn = MySQLdb.connect(**params) # MySQLサーバーに接続
        self.c = self.conn.cursor() # カーソル取得


    def close_spider(self, spider):
        '''
        Spider終了時にMySQLサーバーへの接続を切断
        '''
        self.conn.close()

    
    def process_item(self, item, spider):
        '''
        Itemをnews_tableテーブルに挿入
        '''
        # id 列には自動でprimary key を割り当てるので、挿入列を明示。
        self.c.execute('''
            INSERT INTO news_table (title, body, source, jenre, date_now)
            VALUES (%(title)s, %(body)s, %(source)s, %(jenre)s, %(date_now)s)''', dict(item))
        self.conn.commit() # 変更のコミット

        return item