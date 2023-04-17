import logging
import unittest
from typing import List

import pytest
from cloud_worker.textrank_module.textrank import TextRank

log = logging.getLogger(__name__)



class Test_TextRank:
    keyword_extraction = TextRank().keyword_extraction__undirected
        
    def test_empty_input(self):
        input_text = ""
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert result_only_text == []


    def test_single_word_input(self):
        input_text = "word"
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert result_only_text == ["word"]


    def test_only_punctuation_input(self):
        input_text = ".,?!;"
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        log.warning(result)
        assert result_only_text == []


    def test_repeated_word_input(self):
        input_text = "apple apple apple"
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert result_only_text == ["apple"]


    def test_no_stop_words_input(self):
        input_text = "apple ball cat"
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"apple", "ball", "cat"}


    def test_text_with_stop_words__standard_pos_tags(self):
        input_text = "The quick brown fox jumps over the lazy dog."
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"quick", "brown", "fox", "jumps", "lazy", "dog"}


    def test_text_with_numbers(self):
        input_text = "The 3 little pigs went to the market."
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {'went', "little", "pigs", "market"}
    
    def test_text_with_special_characters(self):
        input_text = "I'm going to @OpenAI's conference!"
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"going", "@OpenAI", "conference"}


    def test_text_with_multiple_sentences(self):
        input_text = "It's a beautiful day. Let's go outside and play!"
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"beautiful", "day", "outside", "play", 'Let'}


    def test_text_with_unusual_spacing(self):
        input_text = "This   text   has\tmultiple\t\tspaces."
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"text", "multiple", "spaces"}
        
        
    @staticmethod
    def convert_nodelist_to_text_list(nodelist: List[dict]):
        return [i['name'] for i in nodelist]
        
    