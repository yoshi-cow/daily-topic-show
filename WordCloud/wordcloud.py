import MySQLdb
import pandas as pd
import MeCab




# mysqlへの接続
connection = MySQLdb.connect(
    host='127.0.0.1', user='news_scraper', passwd='password', db='news_db', charset='utf8mb4'
)
cursor = connection.cursor()

# dbより当日データ取り出し
query = 'SELECT * FROM news_table WHERE DATE(date_now)=CURRENT_DATE()'
cursor.execute(query)
