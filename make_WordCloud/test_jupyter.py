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
import datetime

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
docs_list_lda = []
for i, record in news_df.iterrows():
    docs_list.extend(t.tokenize(record['title-body']))
    docs_list_lda.append(t.tokenize(record['title-body']))


# %%
word_count = pd.Series(docs_list)

# %%
word_list = word_count.value_counts()[:100].to_dict()

plt.figure()
plt.subplot(1,1,1)
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
image = WordCloud(font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',background_color='white').generate_from_frequencies(word_list)
plt.imshow(image)
f_name = '/home/yoshi/work_dir/daily-topic-show/make_WordCloud/wordclud_file/' + str(datetime.date.today()) + '.png'
image.to_file(f_name)



# %%
from gensim.models.word2vec import Word2Vec

# %%
model_path = '/home/yoshi/work_dir/daily-topic-show/make_WordCloud/w2v_model/word2vec.gensim.model'
model = Word2Vec.load(model_path)


# %%

model.wv.similarity('感染', '患者')

# %%
try:
    model.wv.similarity('感染', '感染拡大')
except KeyError as e:
    print(str(e.message))

# %%
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from collections import defaultdict

# %%
# モデル作成
dictionary = Dictionary(docs_list_lda) # 単語とIDの紐付け
dictionary.filter_extremes(no_below=2, no_above=80) # 出現頻度が2文書以下、80%の文書に登場する単語は除外
corpus = [dictionary.doc2bow(text) for text in docs_list_lda] # コーパス作成
lda = LdaModel(corpus=corpus, num_topics=4, id2word=dictionary, random_state=1)



# %%
plt.figure()
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
for t in range(lda.num_topics):
    plt.subplot(1, 1 , t+1)
    x = dict(lda.show_topic(t, 100))
    im = WordCloud(font_path=font_path, background_color='white').generate_from_frequencies(x)
    plt.imshow(im)
    plt.axis("off")
    plt.title("Topic #" + str(t))

# %%
# 各トピックの単語5つを確率が高い順に取得
topic_word_list = []
for t in range(lda.num_topics):
    topic_word_list.append(sorted(dict(lda.show_topic(t, 5)).items(), key=lambda x:x[1], reverse=True))

# %%
len(corpus)

# %%
lda.get_document_topics(corpus[0])

# %%
news_df.head(2)

# %%

topic_df = pd.DataFrame(index=[], columns=['topic', 'prob']) # トピックNo保存用DF
for corpus_text in corpus: # 各記事ごとのトピックNoと、帰属確率取得
    topic_no = lda.get_document_topics(corpus_text)
    topic_df = topic_df.append(pd.Series(topic_no[0], index=topic_df.columns),ignore_index=True)
news_df = news_df.join(topic_df)

# %%
# トピック毎に帰属確率が高い上位３記事を選択
df_sort = news_df.sort_values(['topic', 'prob'], ascending=[True,False]) # トピック毎に帰属確率をソート

# %%
# 各トピックのソート状況チェック
df_sort[df_sort['topic'] == 3][['title', 'topic', 'prob']]

# %%
df_sort.columns

# %%
