#%%
import MySQLdb
import pandas as pd
import MeCab
from urllib import request

import Make_Tokenizer

import matplotlib.pyplot as plt
from wordcloud import WordCloud

import sys
import logging

# %%
### mysqlへの接続
connection = MySQLdb.connect(
    host='127.0.0.1', user='news_scraper', passwd='password', db='news_db', charset='utf8mb4'
)
cursor = connection.cursor()

### レコード保存用DataFrame作成
cols = ['id', 'title', 'body', 'source', 'jenre', 'date_now']
news_df = pd.DataFrame(index=[], columns=cols)

# %%
### dbより当日レコード取り出して、DataFrameへ
query = "SELECT * FROM news_table WHERE date_now='2020-03-04'" 
cursor.execute(query)
if not cursor.rowcount: # レコード有無チェック。レコード無い場合は、エラーログ出力して終了
    logging.error('本日のニュースレコードがありません。')
    connection.close()
    sys.exit(1) # 戻り値は、shell側で終了ステータス確認に利用
for record in cursor:
    news_df = news_df.append(pd.Series((record), index=news_df.columns), ignore_index=True)


# %%
news_df.head(3)

# %%
#   各ニュースサイト固有の不要文字削除
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

# Tokenizerクラスに渡すストップワードリストの作成
#   日本語ストップワードのダウンロード
res = request.urlopen("http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt")
stopwords = [line.decode("utf-8").strip() for line in res]
#   英単語ストップワードのダウンロード
res = request.urlopen("http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/English.txt")
stopwords += [ line.decode("utf-8").strip() for line in res]
stopwords += ['てる', 'いる', 'なる', 'れる', 'する', 'ある', 'こと', 'これ', 'さん', 'して', \
             'くれる', 'やる', 'くださる', 'そう', 'せる', 'した',  '思う', 'いう', 'できる',\
             'それ', 'ここ', 'ちゃん', 'くん', '', 'て','に','を','は','の', 'が', 'と', 'た', 'し', 'で', \
             'ない', 'も', 'な', 'い', 'か', 'ので', 'よう', '', '()', \
             'Nothing']



# %%
t = Make_Tokenizer.Tokenizer(stopwords)


# %%
connection.close()

# %%
news_df.fillna({'body':'Null'}, inplace=True)
news_df['title-body'] = news_df['title'] +'。'+ news_df['body']

# %%
docs_list = []
for i, record in news_df.iterrows():
    docs_list.extend(t.tokenize(record['title-body']))


# %%
word_count = pd.Series(docs_list)

# %%
word_list = word_count.value_counts()[:100].to_dict()

plt.figure()
plt.subplot(1,1,1)
image = WordCloud(font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',background_color='white').generate_from_frequencies(word_list)
plt.imshow(image)
image.to_file()



# %%
# import datetime
f_name = '/home/yoshi/work_dir/daily-topic-show/make_WordCloud/wordclud_file/' + str(datetime.date.today()) + '.png'

# %%
f_name


# %%
image.to_file(f_name)

# %%
