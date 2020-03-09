#%%
import MySQLdb
import pandas as pd
import numpy as np
from urllib import request

import MeCab
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from wordcloud import WordCloud

import Make_Tokenizer

import sys
import logging
import datetime




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
cols = ['id', 'title', 'body', 'source', 'jenre', 'date_now']
news_df = pd.DataFrame(index=[], columns=cols)


### dbより当日レコード取り出して、DataFrameへ
query = 'SELECT * FROM news_table WHERE DATE(date_now)=CURRENT_DATE()'
cursor.execute(query)
if not cursor.rowcount: # レコード有無チェック。レコード無い場合は、エラーログ出力して終了
    logging.error('本日のニュースレコードがありません。')
    connection.close()
    sys.exit(1) # 戻り値は、shell側で終了ステータス確認に利用
for record in cursor:
    news_df = news_df.append(pd.Series((record), index=news_df.columns), ignore_index=True)


### レコード前処理ー各ニュース記事に以下の前処理実施 
#   各ニュースサイト固有の不要文字削除
#   英単語は全て小文字へ
#   全角カタカナ、半角カタカナの表記ゆれ
#   全角数字を半角数字へ
#   全角記号（）、ーなどの削除
#   数値の削除
#   日本語・英語のストップワード削除
#   WordNetによる単語の統一
#   タイトルと内容を一つにまとめる

# 各ニュースサイト固有の不要文字削除
news_df['body'] = news_df['body'].str.replace("この記事は有料記事です。","")
news_df['body'] = news_df['body'].str.replace("いますぐ登録して続きを読む", "")
news_df['body'] = news_df['body'].str.replace("登録済みの方はこちら", "")
news_df['body'] = news_df['body'].str.replace("文字サイズ", "")
news_df['body'] = news_df['body'].str.replace("印刷", "")
news_df['body'] = news_df['body'].str.replace("連載をフォロー", "")
news_df['body'] = news_df['body'].str.replace("［PR］", "")
news_df['body'] = news_df['body'].str.replace("PR", "")
news_df['body'] = news_df['body'].str.replace("あわせて読みたい", "")
news_df['body'] = news_df['body'].str.replace("【随時更新】", "")
news_df['body'] = news_df['body'].str.replace(r"cX\.callQueue\.push\(\['invoke',function\(\)\{", "")
news_df['body'] = news_df['body'].str.replace(r"googletag\.cmd\.push\(function\(\) \{ googletag\.display\('PC-article-rec_kijinaka'\); \}\);", "")
news_df['body'] = news_df['body'].str.replace(r"\}\]\);", "")
news_df['body'] = news_df['body'].str.replace(r"googletag\.cmd\.push\(function\(\) \{ googletag\.display\('div-gpt-ad-Rec_Article'\);\ \}\);", "")
news_df['body'] = news_df['body'].str.replace(r"googletag\.cmd\.push\(function\(\) \{ googletag\.display\('div-gpt-ad-Inread'\); \}\);", "")
news_df['body'] = news_df['body'].str.replace(r"googletag\.cmd\.push\(function\(\) \{", "")
news_df['body'] = news_df['body'].str.replace(r"googletag\.display\('ad_dfp_premiumrec'\);", "")
news_df['body'] = news_df['body'].str.replace(r"\}\);", "")

# bodyがNull値だと文字列と連結できないので文字Nothingで置き換えとく(Nothingは、Stopwordに入れて後で削除する)
news_df.fillna({'body':'Nothing'}, inplace=True) 
# タイトルと記事まとめて分析対象なので、タイトルと記事をひとつにまとめる
news_df['title-body'] = news_df['title'] + '。' + news_df['body']

# Tokenizerクラスに渡すストップワードリストの作成
#   日本語ストップワード
res = request.urlopen("http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt")
stopwords = [line.decode("utf-8").strip() for line in res]
#   英単語ストップワード
res = request.urlopen("http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/English.txt")
stopwords += [ line.decode("utf-8").strip() for line in res]
#   追加ストップワード
stopwords += ['てる', 'いる', 'なる', 'れる', 'する', 'ある', 'こと', 'これ', 'さん', 'して', \
            'くれる', 'やる', 'くださる', 'そう', 'せる', 'した',  '思う', 'いう', 'できる',\
            'それ', 'ここ', 'ちゃん', 'くん', '', 'て','に','を','は','の', 'が', 'と', 'た', 'し', 'で', \
            'ない', 'も', 'な', 'い', 'か', 'ので', 'よう', '', '()', \
            'Nothing', '年月', '月日', '出る']


### 単語の出現数を求めてWordCloudで可視化後、pngファイルで保存
# 分かち書き処理
t = Make_Tokenizer.Tokenizer(stopwords)
docs_list = []
for _, record in news_df.iterrows():
    docs_list.append(t.tokenize(record['title-body'])) # トピックモデル用

# wordcloud用ldaモデル作成（トピック数１でモデル作成しWordCloudに結果を渡す）
dictionary = Dictionary(docs_list) # 単語とIDの紐付け
dictionary.filter_extremes(no_below=2, no_above=80) # 出現頻度が2文書以下、80%の文書に登場する単語は除外
corpus = [dictionary.doc2bow(text) for text in docs_list] # コーパス作成
lda = LdaModel(corpus=corpus, num_topics=1, id2word=dictionary, random_state=1)

# wordcloudの作成と保存
image = WordCloud(font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', \
                    background_color='white').generate_from_frequencies(dict(lda.show_topic(0, 100)))
f_name = '/home/yoshi/work_dir/daily-topic-show/make_WordCloud/wordclud_file/' + TODAY + '.png'
image.to_file(f_name)

# 


### トピックモデルで関連ワードごとにニュースをまとめ、tweet用にデータをMySQLに保存
# 記事分類用ldaモデル作成（トピック数は３。データ少ないし、ツィート数の上限もあるので３でも厳しいかも・・・）
# ※学習データがかなり少ないので、残念ながら精度は厳しい・・・
lda = LdaModel(corpus=corpus, num_topics=4, id2word=dictionary, random_state=1) #------------------------------------------
# 各トピックの単語３つを確率が高い順に取得
topic_word_list = []
for t in range(lda.num_topics):
    topic_word_list.append(sorted(dict(lda.show_topic(t, 3)).items(), key=lambda x:x[1], reverse=True))

# 記事ごとのトピックと帰属確率を取得してnews_dfに追加
topic_df = pd.DataFrame(index=[], columns=['topic', 'prob']) # トピックNo保存用DF
for corpus_text in corpus: # 各記事ごとのトピックNoと帰属確率を取得
    topic_no = lda.get_document_topics(corpus_text)
    topic_df = topic_df.append(pd.Series(topic_no[0], index=topic_df.columns),ignore_index=True)
news_df = news_df.join(topic_df)
df_sort = news_df.sort_values(['topic', 'prob'], ascending=[True,False]) # トピック毎に帰属確率をソート

# 取得した単語をdfへ
word_df = pd.DataFrame(index=[], columns=['word_1', 'word_2', 'word_3'])
for topic in topic_word_list:
    words = []
    for word in topic:
        words.append(word[0])
    word_df = word_df.append(pd.Series(words, index=word_df.columns), ignore_index=True) 

# トピック毎に帰属確率が最も高い記事２つを選択
url_df = pd.DataFrame(index=[], columns=['title_1', 'source_1', 'title_2', 'source_2'])

# トピックごとの記事titleとsource抽出
for i in range(4): # トピック数がrange()の引数 #------------------------------------------
    temp_df = df_sort[df_sort['topic'] == i] # 該当トピックのdf取得
    td_1 = pd.Series(list(temp_df.iloc[0, [1,3]]), index=['title_1', 'source_1']) # 確率最大の記事取得
    if temp_df.iloc[1, 8] >= 0.985: # ２番めの記事は帰属確率が98.5%以上なら取得
        td_2 = pd.Series(list(temp_df.iloc[1, [1,3]]), index=['title_2', 'source_2'])
    else:
        td_2 = pd.Series([np.nan, np.nan], index=['title_2', 'source_2'])
    td_c = pd.concat([td_1, td_2])
    url_df = url_df.append(td_c, ignore_index=True)

# tweet用データ作成日追加
url_df['date_now'] = df_sort.iloc[0,5]

# 単語ｄｆとタイトルｄｆまとめて、tweet_tableに保存
tw_df = word_df.join(url_df, how='outer') # ２番めのタイトルが無い場合に備えて外部結合

# MySQLにtweet用データ保存
try:
    # tweet_tableに保存
    for i, record in tw_df.iterrows():
        index_dic = {'topic_no': i}
        record_dic = record.to_dict()
        if type(record_dic['title_2']) == float:
            # np.nan(float型)はSQLにINSERTできないのでNoneに置換する
            record_dic['title_2'] = None
            record_dic['source_2'] = None
        record_dic.update(index_dic)
        query = '''INSERT INTO tweet_table 
                    (topic_no, word_1, word_2, word_3,
                    title_1, source_1, title_2, source_2, date_now)
                    VALUES (%(topic_no)s, %(word_1)s, %(word_2)s, %(word_3)s,
                    %(title_1)s, %(source_1)s, %(title_2)s, %(source_2)s, %(date_now)s) '''
        cursor.execute(query, record_dic)
    connection.commit()
except MySQLdb.Error as e:
    # エラー内容出力して終了
    erro_me = 'tweet_table保存エラー発生！' + str(e)
    logging.error(erro_me)
    connection.close()
    sys.exit(2) # 戻り値は、shell側で終了ステータス確認に利用

### 接続閉じる
connection.close()


# %%
