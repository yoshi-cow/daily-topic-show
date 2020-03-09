# 分かち書きして、対象単語のみ取り出すTokenizerクラスの作成
# 処理内容
#   英単語を大文字から小文字へ
#   分かち書きする
#   名詞、動詞、形容詞のみ抽出
#   ストップワードを除外

import MeCab
import re

class Tokenizer:

    def __init__(self, stopwords, parser=None, include_pos=None, exclude_posdetail=None, exclude_reg=None):
        '''
        stopwords: ストップワードのリスト
        parser: mecabがデフォルト。別のパーサーを指定したときに利用
        include_pos: 抽出対象の品詞リスト。デフォルトは、['名詞', '動詞', '形容詞']
        exclude_posdetail: 除外対象の詳細品詞("固有名詞"とか、"格助詞"など)。デフォルトは、['接尾', '数']
        exclude_reg: 除外対象文字を正規表現で指定できる。例) r"\d(年|月|日) 指定で年月日を削除できる。
        '''
        self.stopwords = stopwords
        self.include_pos = include_pos if include_pos else ['名詞', '動詞', '形容詞']
        self.exclude_posdetail = exclude_posdetail if exclude_posdetail else ['接尾', '数']
        self.exclude_reg = exclude_reg if exclude_reg else r"$^"

        if parser:
            self.parser = parser
        else:
            # MeCab.Tager("-Ochasen")指定すると、分かち書き結果の出力形式が -Ochasen 無しと異なるので注意
            mecab = MeCab.Tagger('-Ochasen -d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd')
            self.parser = mecab.parse

    def tokenize(self, text, show_pos=False):
        '''
        - 引数の記事本文から、対象単語のリストを抽出して返す。
        text: 一つの記事
        show_pos: 単語の品詞も同時に表示するかの指定。
            False: 単語のみのリスト
            True: (単語, 品詞)のタプルのリストになる。
        '''
        text = re.sub(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", "", text) # URLの削除
        text = re.sub(r"\"?([-a-zA-Z0-9.`?{}]+\.jp)\"?" ,"", text)  # xxx.jpの削除
        text = text.lower() # 英字の小文字化
        text = re.sub(r"([0-9０-９])", "", text) # 半角、全角数字の削除

        # 記事(text)をMeCab.parseでパースしたのを改行(\n)でパースして一行毎にし、それをさらにタブ(\t)でsplitしてリスト化する。
        # l の中身：textが、'メカブって神ってる' の場合
        # [
        #    ['メカブ', 'メカブ', 'MeCab', '名詞-固有名詞-一般', '', ''],
        #    ['って', 'ッテ', 'って', '助詞-格助詞-連語', '', ''],
        #    ['神ってる', 'カミッテル', '神ってる', '名詞-固有名詞-一般', '', ''],
        #    ['EOS'],
        #    ['']
        # ]
        l = [line.split("\t") for line in self.parser(text).split("\n")]

        # lから一行(単語一つのパース結果のリスト)ずつ取り出し、
        # そのリストの要素数が4つ以上なら、品詞のある単語なので、抽出チェックする
        # i ：単語一つのパース結果のリスト：['神ってる', 'カミッテル', '神ってる', '名詞-固有名詞-一般', '', '']
        # i[2] : 単語自身
        # i[3] : 単語の品詞： '名詞-固有名詞-一般'
        # i[3].split("-")[0] in self.include_pos : 単語の品詞が対象かのチェック
        # i[3].split("-")[1] not in self.exclude_posdetail : 単語の詳細品詞が、除外対象かチェック
        # not re.search(r"(-|−)\d", i[2]) : 単語が -数字, −数字 なら除外
        # not re.search(self.exclude_reg, i[2]) : 単語が除外正規表現に当てはまるかのチェック
        # i[2] not in self.stopwords : 単語がストップワードかのチェック
        # res 中身例１（show_pos=Falseの時)：['MeCab', 'って', '神ってる']
        # res 中身例２（show_pos=Trueの時)：[('MeCab', '名詞-固有名詞-一般'), ('って', '助詞-格助詞-連語'), ('神ってる', '名詞-固有名詞-一般')]        
        res = [
            i[2] if not show_pos else (i[2], i[3]) for i in l
                if len(i) >= 4 # 品詞があるとき
                    and i[3].split("-")[0] in self.include_pos
                    and i[3].split("-")[1] not in self.exclude_posdetail
                    and not re.search(r"(-|−)\d", i[2])
                    and not re.search(self.exclude_reg, i[2])
                    and i[2] not in self.stopwords
            ] 
        return res
     

