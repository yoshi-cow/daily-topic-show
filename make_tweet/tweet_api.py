import tweepy

import os

# MySQLよりワードとurl抽出



# OAuth設定
auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
auth.set_access_token(os.environ['ACCESS_TOKEN'],os.environ['ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth)

# ツィート文作成
tweet = '''
    てすとてすとてすとてすと\n
    ■てすと　テスト　試験\n
    url:.........  ur::.......\n
    ■てすと２　テスト２　試験２\n
    url:.........  url:........\n
    ■テスト３　てすと３　試験３\n
    url:.........   url:........\n
    '''
# tweet文文字数チェック


# 画像添付
f_name = "/home/yoshi/work_dir/daily-topic-show/make_WordCloud/wordclud_file/2020-03-08.png"

api.update_with_media(filename=f_name, status=tweet)