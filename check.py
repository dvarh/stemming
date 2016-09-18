# -*- coding: utf-8 -*-
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import RussianStemmer
from nltk.corpus import stopwords
import string
import sqlite3
import itertools
import codecs
import argparse
import os
import multiprocessing as mp
import datetime
from collections import Counter

f_path = '/Volumes/HDD/Users/dvarh/Downloads/task/text_files/0508.txt'
dbname = 'sqlite.db'


def ru_word(word):
    ru = set(u"БбвГгДдЁёЖжЗзИиЙйЛлмнПптУФфЦцЧчШшЩщЪъЫыЬьЭэЮюЯя")
    return any(c in ru for c in word)


def en_word(word):
    en = set(u"DdFfGghIiJjLlNQqRrSstUVvWwYZz")
    return any(c in en for c in word)


def normalize(word):
    rus = u"АаВЕеКкМНОоРрСсТуХх@пь"
    eng = u"AaBEeKkMHOoPpCcTyXxanb"
    if ru_word(word):
        if any(c in set(eng) for c in word):
            pass
        for i in xrange(len(rus)):
            word = word.replace(eng[i], rus[i])
        return word

    if en_word(word):
        for i in xrange(len(eng)):
            if any(c in set(rus) for c in word):
                pass
            word = word.replace(rus[i], eng[i])
        return word

    return word


def normalize_tokens(tokens):
    right_words = []

    is_rouge = False
    for word in tokens:
        new_word = normalize(word)
        is_rouge = new_word != word or is_rouge
        right_words.append(new_word)

    return is_rouge, right_words


def tokenize(file_text):
    # firstly let's apply nltk tokenization
    tokens = word_tokenize(file_text)

    # cleaning words
    tokens = [i.replace(u"«", u"").replace(u"»", u"") for i in tokens]

    # let's delete punctuation symbols
    tokens = [i for i in tokens if (i not in string.punctuation)]

    # deleting stop_words
    stop_words = stopwords.words('russian') + [u'·', u'-', u'', u'--', u'-', u'...', u'р/шт', u'шт', u'р', u'мм', u'см']
    tokens = [i for i in tokens if (i.lower() not in stop_words)]

    # cleaning digits
    tokens = [i for i in tokens if (not i.isdigit())]

    return tokens


def stemming(tokens):
    stemmer = RussianStemmer()
    return [stemmer.stem(t) for t in tokens]


def academic_nausea(filepath):
    with codecs.open(filepath, "r", "utf-8") as input_file:
        raw_text = input_file.read()
    tokens = tokenize(raw_text)
    if not tokens:
        return os.path.basename(filepath), False, 0
    is_rouge, tokens = normalize_tokens(tokens)
    words = stemming(tokens)
    word_counters = Counter(words)
    nausea = 100 * float(sum((i[1] for i in word_counters.most_common(5)))) / float(sum(word_counters.itervalues()))
    return os.path.basename(filepath), is_rouge, nausea


def process_advertisement(working_dir, processes_count):
    if not os.path.exists(working_dir):
        print u"Path doesn't exist '%s'" % working_dir
        return

    processed_files = get_processed_files()

    files = [os.path.join(working_dir, f)
             for f in os.listdir(working_dir) if f.endswith(".txt") and f not in processed_files]
    if len(files) == 0:
        print u"Nothing to process in %s" % working_dir
        return

    pool = mp.Pool(processes_count)
    imap_unordered = pool.imap_unordered(academic_nausea, files)

    for r in imap_unordered:
        save_to_db(r)


def main():
    parser = argparse.ArgumentParser(description='Check advertisement')
    parser.add_argument('--path', '-p', help='Path to unpacked apps', required=True)
    parser.add_argument('--number', '-n', type=int, help='Count of process', required=True)
    args = parser.parse_args()
    processes_count = args.number

    init_db()
    process_advertisement(args.path,  processes_count)


def init_db():
    create_sql = """
CREATE TABLE IF NOT EXISTS 'academic_nausea' (
    'filename'	TEXT NOT NULL,
    'is_rouge'	INTEGER NOT NULL,
    'nausea'	REAL NOT NULL
)"""
    with sqlite3.connect(dbname) as conn:
        cursor = conn.cursor()
        cursor.execute(create_sql)


def get_processed_files():
    get_sql = """
SELECT filename FROM academic_nausea
"""
    with sqlite3.connect(dbname) as conn:
        cursor = conn.cursor()
        cursor.execute(get_sql)
        res = cursor.fetchall()

    return list(itertools.chain(*res))


def save_to_db(row):
    save_sql = """
INSERT INTO academic_nausea
(filename, is_rouge, nausea) VALUES(?,?,?);
"""
    with sqlite3.connect(dbname) as conn:
        cursor = conn.cursor()
        cursor.execute(save_sql, row)


if __name__ == '__main__':
    dt = datetime.datetime.now()
    main()
    print(datetime.datetime.now() - dt)
