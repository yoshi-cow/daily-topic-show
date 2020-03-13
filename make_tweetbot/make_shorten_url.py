import requests
import os
import logging

def shorten_url(longurl):
    '''
    bitlyを使用
    下のコードは、Ver3で作成。後でVer4に対応必要かも
    '''
    # エラーログ設定
    Err_Format = '[%(asctime)s]%(filename)s(%(lineno)d): %(message)s'
    logging.basicConfig(
        filename='/home/yoshi/work_dir/daily-topic-show/Error.log',
        format=Err_Format,
        datefmt='%Y-%m-%d %H:%M:%S', 
        level=logging.WARNING
    )

    # bitlyアクセスurl
    bitly_url = 'https://api-ssl.bitly.com/v3/shorten'

    query = { 'access_token': os.environ['BITLY_TOKEN'], 'longurl':longurl}

    # 短縮url作成
    try:
        result = requests.get(bitly_url, params=query).json()['data']['url']
    except:
        logging.error('requests.get()エラー、または、短縮url作成に失敗しました。')
        result = None

    return result
