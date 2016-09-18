# -*- coding: utf-8 -*-
import unittest
from check import *


class StemmingTestCase(unittest.TestCase):
    def test_ru_word(self):
        self.assertTrue(ru_word(u'Буква'))
        self.assertTrue(ru_word(u'Буквa'))
        self.assertFalse(ru_word(u'Сурок'))

    def test_en_word(self):
        self.assertTrue(en_word(u'some'))
        self.assertTrue(en_word(u'sоme'))
        self.assertFalse(en_word(u'back'))

    def test_normalize(self):
        self.assertEqual(u'some', normalize(u'sоme'))
        self.assertEqual(u'some', normalize(u'some'))

        self.assertEqual(u'Буква', normalize(u'Буквa'))
        self.assertEqual(u'Буква', normalize(u'Буква'))

        self.assertEqual(u'540x550', normalize(u'540x550'))

    def test_normalize_tokens(self):
        tokens = [u'Буква', u'Буквa', u'sоme', u'some']
        expected_tokens = [u'Буква', u'Буква', u'some', u'some']
        is_rouge , res = normalize_tokens(tokens)
        self.assertEqual(expected_tokens, res)
        self.assertTrue(is_rouge)

        tokens = [u'Буква', u'some', u'540x550']
        expected_tokens = [u'Буква', u'some', u'540x550']
        is_rouge , res = normalize_tokens(tokens)
        self.assertEqual(expected_tokens, res)
        self.assertFalse(is_rouge)


    def test_tokenize(self):
        text = u"""Рассмотрим спокойную, семейную пару без животных и детей.
        · 150 р/шт шт. р.
        750 мм
        -- 150 см
"""
        tokens = [u'Рассмотрим', u'спокойную', u'семейную', u'пару', u'животных', u'детей']
        self.assertEqual(tokens, tokenize(text))

    def test_stemming(self):
        tokens = [u'Рассмотрим', u'семейная',  u'спокойную', u'семейную', u'пару', u'животных', u'детей']
        words = [u'рассмотр', u'семейн', u'спокойн', u'семейн', u'пар', u'животн', u'дет']
        self.assertEqual(words, stemming(tokens))

    def test_academic_nausea(self):
        self.assertEqual(('test.txt', False, 12.056737588652481), academic_nausea('test.txt'))
        self.assertEqual(('empty_test.txt', False, 0), academic_nausea('empty_test.txt'))
        self.assertEqual(('rouge_text.txt', True, 12.056737588652481), academic_nausea('rouge_text.txt'))

