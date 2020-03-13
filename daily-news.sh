#!/bin/bash

# ニュースサイトからメインニュースを抽出し、WordCloudで重要単語を可視化後、
# 重要単語関連記事のリンクとWordclud画像をツイートする
# 毎朝、cronにて自動実行

### メインニュース抽出 ###
. /home/yoshi/anaconda3/etc/profile.d/conda.sh # shell script上でcondaコマンド実行するための処理
conda activate daily # 仮想環境アクティベイト
# 各サイトよりニュースを抽出しMySQLに保存
cd /home/yoshi/work_dir/daily-topic-show/crawl_news
scrapy crawl asa -s RETRY_TIMES=1
scrapy crawl mai -s RETRY_TIMES=1
scrapy crawl san -s RETRY_TIMES=1
scrapy crawl yom -s RETRY_TIMES=1

. ~/work_dir/ex.sh

### WordCloudの作成とtweet用データの作成 ###
if test $? -eq 0
then
    python /home/yoshi/work_dir/daily-topic-show/make_WordCloud/m_wordcloud.py
fi

### tweetを作成し、twitterに投稿 ###
# 実行日のWordCloud画像ファイルがあれば実行
WCfile=`date "+%Y-%m-%d"`.png
if test -f /home/yoshi/work_dir/daily-topic-show/make_WordCloud/wordclud_file/$WCfile
then
    python /home/yoshi/work_dir/daily-topic-show/make_tweetbot/tweet_api.py
fi

conda deactivate