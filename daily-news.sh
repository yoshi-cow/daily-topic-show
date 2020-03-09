#!/bin/bash

# ニュースサイトからメインニュースを抽出し、WordCloudで重要単語を可視化後、
# メインニュースの要約を作成

### メインニュース抽出 ###
. /home/yoshi/anaconda3/etc/profile.d/conda.sh # shell script上でcondaコマンド実行するための処理
conda activate daily # 仮想環境アクティベイト
# 各サイトよりニュースを抽出しMySQLに保存
cd /home/yoshi/work_dir/daily-topic-show/crawl_news
scrapy crawl asa 
scrapy crawl mai
scrapy crawl san
scrapy crawl yom


### WordCloudの作成とtweetデータの作成 ###
if test $? -eq 0
then
    python /home/yoshi/work_dir/daily-topic-show/make_WordCloud/m_wordcloud.py
fi


### twitterに投稿 ###
# WordCloud画像ファイルがあれば実行
WCfile=`date "+%Y-%m-%d"`.png
if test -f /home/yoshi/work_dir/daily-topic-show/make_WordCloud/wordclud_file/$WCfile
then
    # WordCloudファイルを投稿
    cd /home/yoshi/work_dir

fi

conda deactivate