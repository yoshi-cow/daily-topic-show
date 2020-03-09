#%%
import MySQLdb
import pandas as pd
import os
import sys
import logging
import datetime
import time
import re

import tweepy
from make_shorten_url import shorten_url

# %%
TODAY = str(datetime.date.today()) # ファイル名用定数

### エラーログ設定
Err_Format = '[%(asctime)s]%(filename)s(%(lineno)d): %(message)s'
logging.basicConfig(
    filename='/home/yoshi/work_dir/daily-topic-show/Error.log',
    format=Err_Format,
    datefmt='%Y-%m-%d %H:%M:%S', 
    level=logging.WARNING
)


### mysqlへの接続
connection = MySQLdb.connect(
    host='127.0.0.1', user='news_scraper', passwd='password', db='news_db', charset='utf8mb4'
)
cursor = connection.cursor()


### レコード保存用空DataFrame作成
cols = ['id', 'topic_no', 'word_1', 'word_2', 'word_3', 'title_1','source_1','title_2','source_2','date_now']
tweet_df = pd.DataFrame(index=[], columns=cols)


### dbより当日レコード取り出して、DataFrameへ

# dbから抽出
query = 'SELECT * FROM tweet_table WHERE DATE(date_now)=CURRENT_DATE()'
try:
    cursor.execute(query)
except MySQLdb.Error as e:
    # エラー内容出力して終了
    erro_me = 'tweet_table抽出エラー!' + str(e)
    logging.error(erro_me)
    connection.close()
    sys.exit(3) # 戻り値は、shell側で終了ステータス確認に利用

# レコード有無チェック。レコード無い場合は、エラーログ出力して終了
if not cursor.rowcount:
    logging.error('本日のtweet用レコードがありません。')
    connection.close()
    sys.exit(4) # 戻り値は、shell側で終了ステータス確認に利用
for record in cursor:
    tweet_df = tweet_df.append(pd.Series((record), index=tweet_df.columns), ignore_index=True)

#%% ------------------------------------------------------
### 短縮url作成してtweet_dfに挿入
# 短縮url保存用df
cols = ['url_1', 'url_2']
url_df = pd.DataFrame(index=[],columns=cols)

# sourceがあったらurlを短縮
for _, record in tweet_df.iterrows():
    url_list = []
    if record['source_1']:
        shoten = shorten_url(record['source_1'])
        url_list.append(shoten)
        time.sleep(1) # bitlyアクセス負荷軽減用
        if record['source_2']:
            shoten = shorten_url(record['source_2'])
            url_list.append(shoten)
            time.sleep(1) # bitlyアクセス負荷軽減用
        else:
            url_list.append(None)
    else:
        url_list.extend([None, None])
    url_df = url_df.append(pd.Series(url_list, index=url_df.columns), ignore_index=True)
# merge
tweet_df = tweet_df.join(url_df)

#%%
#--------------------
# OAuth設定
auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
auth.set_access_token(os.environ['ACCESS_TOKEN'],os.environ['ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth)

#%%

# ツィート文作成
tweet = ''
for _, record in tweet_df.iterrows():
    # 単語取り出し
    word_list = '/'.join(list(record[2:5]))
    word_list += '->'
    # 短縮url取り出し
    if record['url_2']:
        # urlがurl_2にも有るとき
        url_list = '  '.join(list(record[-2:])) + '\n'
    else:
        # urlがurl_1にしか無いとき
        url_list = record['url_1'] + '\n'
    tweet = tweet + word_list + url_list # 単語とurl連結

tweet = tweet[:-1] # 最後の'\n'削除


# 画像添付
f_name = "/home/yoshi/work_dir/daily-topic-show/make_WordCloud/wordclud_file/" + TODAY + ".png"


#%%
# tweetと画像を投稿
try:
    api.update_with_media(filename=f_name, status=tweet)
except tweepy.TweepError as e:
    # エラー内容ログ出力
    err_me = '文字数オーバーエラー！単語数減らして出力' + str(e)
    logging.error(err_me)
    # tweet文字数オーバーなので文字数減らす。（最初の３単語とurlを除く）
    s_o = re.search(r'\n', tweet)
    tweet = tweet[s_o.start()+1:]
    try:
        time.sleep(1) # twitter api負荷軽減用
        api.update_with_media(filename=f_name, status=tweet)
    except tweepy.TweepError as e:
        err_me = 'tweet投稿エラー!' + str(e)
        logging.error(err_me)
        connection.close()
        sys.exit(5) # 戻り値は、shell側で終了ステータス確認に利用


### DBのcommenction閉じる
connection.close()



# %%
