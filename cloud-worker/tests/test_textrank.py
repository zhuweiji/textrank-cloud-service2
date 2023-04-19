import logging
import unittest
from typing import Dict, List

import networkx as nx
import numpy as np
import pytest

from cloud_worker.textrank_module.textrank import TextRank

log = logging.getLogger(__name__)

"""
fix algo
    convergence
    normalised values

hyperparams:
    keyword extraction  (?)
   
    damping factor (0.85 in paper) 
    convergence threshold (0.0001 in paper)
    co-occurence relation 2-10 (2 in paper)
    pos tags -: all open class words, nouns and verbs only (nouns, adjs in paper)
    number of keywords output - T (1/3 of tokens in paper)

large state space
   
"""
            

class Test_TextRank_Sentence_Extraction:
    sentence_extraction = TextRank().sentence_extraction__undirected
    
    def test_sample_text(self):
        # input_text = "When talking about words with similar meaning, you often read about the distributional hypothesis in linguistics. This hypothesis states that words bearing a similar meaning will appear between similar word contexts. You could say “The box is on the shelf.”, but also “The box is under the shelf.” and still produce a meaningful sentence. On and under are interchangeable up to a certain extent."
        # input_text = "When talking about words with similar meaning, you often read about the distributional hypothesis in linguistics. This hypothesis states that words bearing a similar meaning will appear between similar word contexts. You could say “The box is on the shelf.”, but also “The box is under the shelf.” and still produce a meaningful sentence. On and under are interchangeable up to a certain extent."
        input_text = """Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types systems and systems of mixed types."""
        

        sents = [TextRank().nlp(i) for i in input_text.split('. ')]

        nodes = TextRank()._generate_nodes_from_similarity(sents)
        edge_75_percentile = np.percentile(
            [[edge.weight] for node in nodes for edge in node.connected],
            75)
        log.warning(edge_75_percentile)
        n = {node.id: [i.get_other(node).id for i in node.connected if i.weight > edge_75_percentile] for node in nodes}
        log.warning(n)
        g = nx.Graph(n)
        log.warning([i for i in nx.connected_components(g)])
        
        # result = self.sentence_extraction(input_text)
        assert False

class Test_TextRank__Keyword_Extraction:
    keyword_extraction    = TextRank().keyword_extraction__undirected
    regenerate_keyphrases = TextRank().regenerate_keyphrases
    
    
    def test_example_from_textrank_paper(self):
        input_text = """Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types systems and systems of mixed types."""

        results_from_paper = {
        "linear constraints":1,
        "linear diophantine equations":1,
        "natural numbers":1,
        "nonstrict inequations":1,
        "strict inequations":1,
        "upper bounds":1,
        }
        
        partial_result = self.keyword_extraction(input_text)
        assert partial_result
        
        only_text_and_score:Dict[str, int] = {i['name']: i['score'] for i in partial_result} # type: ignore
        
        result = self.regenerate_keyphrases(only_text_and_score, input_text)
        sorted_result = sorted(result.items(), key=lambda x: x[1])
        
        assert set(results_from_paper.keys()) - set(result.keys()) == set()
    
        
    @staticmethod
    def convert_nodelist_to_text_list(nodelist: List[dict]):
        return [i['name'] for i in nodelist]
    

class Test_TextRank__Keyword_Extraction__No_Keyphrase_Regeneration:
    keyword_extraction = TextRank().keyword_extraction__undirected
    extended_pos_tags = ['NOUN','ADJ', 
                         'PROPN',
                        'VERB','ADV'
                        ]
    convert_nodelist_to_text_list = lambda self, v: Test_TextRank__Keyword_Extraction.convert_nodelist_to_text_list(v)
        
    def test_example_from_textrank_paper(self):
        input_text = """Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types systems and systems of mixed types."""

        result_in_paper = {"types","systems","linear","diophantine","constraints","system","compatibility","criteria","numbers","natural","equations","strict","inequations","nonstrict","upper","bounds","components","algorithms","solutions","sets","minimal","construction"}
        expected_result = {'components', 'compatibility', 'numbers', 'inequations', 'criteria', 'upper', 'nonstrict', 'constraints', 'systems', 'generating', 'solutions', 'natural', 'bounds', 'minimal', 'set', 'algorithms', 'equations', 'types', 'construction', 'linear', 'diophantine', 'strict'}

        result = self.keyword_extraction(input_text, number_to_keep=len(expected_result))
        result_only_text = self.convert_nodelist_to_text_list(result)
        result_only_text = [i.lower() for i in result_only_text]
        
        assert set(result_only_text) == expected_result
    
    def test_empty_input(self):
        input_text = ""
        
        result = self.keyword_extraction(input_text)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert result_only_text == []


    def test_single_word_input(self):
        input_text = "word"
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text))
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert result_only_text == ["word"]


    def test_only_punctuation_input(self):
        input_text = ".,?!;"
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text))
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        log.warning(result)
        assert result_only_text == []


    def test_repeated_word_input(self):
        input_text = "apple apple apple"
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text))
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert result_only_text == ["apple"]


    def test_no_stop_words_input(self):
        input_text = "apple ball cat"
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text))
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"apple", "ball", "cat"}


    def test_text_with_stop_words__extended_pos_tags(self):
        input_text = "The quick brown fox jumps over the lazy dog."
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text),
                                         pos_tags=self.extended_pos_tags)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"quick", "brown", "fox", "jumps", "lazy", "dog"}


    def test_text_with_numbers(self):
        input_text = "The 3 little pigs went to the market."
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text),
                                         pos_tags=self.extended_pos_tags)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {'went', "little", "pigs", "market"}
    
    def test_text_with_special_characters(self):
        input_text = "I'm going to @OpenAI's conference!"
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text),
                                         pos_tags=self.extended_pos_tags)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"going", "@OpenAI", "conference"}


    def test_text_with_multiple_sentences(self):
        input_text = "It's a beautiful day. Let's go outside and play!"
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text),
                                         pos_tags=self.extended_pos_tags)
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"beautiful", "day", "outside", "play", 'Let'}


    def test_text_with_unusual_spacing(self):
        input_text = "This   text   has\tmultiple\t\tspaces."
        
        result = self.keyword_extraction(input_text, number_to_keep=len(input_text))
        result_only_text = self.convert_nodelist_to_text_list(result)
        
        assert set(result_only_text) == {"text", "multiple", "spaces"}
        
        



class Test_TextRank_Utils:
    regenerate_keyphrases = TextRank().regenerate_keyphrases
    
    def test_regenerate_keyphrases(self):
        input_text = 'a b c'
        keywords = {'a': 1, 'b': 1}
        expected_results = {'a b':1}
        
        result = self.regenerate_keyphrases(keywords, input_text)
        
        assert result == expected_results

    def test_regenerate_keyphrases__empty_keywords(self):
        input_text = 'apple banana cherry'
        keywords = {}
        expected_results = {}

        result = self.regenerate_keyphrases(keywords, input_text)

        assert result == expected_results


    def test_regenerate_keyphrases__empty_split_text(self):
        input_text = ''
        keywords = {'apple': 1, 'banana': 2}
        expected_results = {}

        result = self.regenerate_keyphrases(keywords, input_text)

        assert result == expected_results


    def test_regenerate_keyphrases__no_keyphrases(self):
        input_text = 'apple banana cherry'
        keywords = {'orange': 2, 'grape': 1}
        expected_results = {}

        result = self.regenerate_keyphrases(keywords, input_text)

        assert result == expected_results


    def test_regenerate_keyphrases__single_keyword(self):
        """single word phrases are discarded, as we only want multiword phrases"""
        input_text = 'apple banana cherry'
        keywords = {'apple': 1}
        expected_results = {}

        result = self.regenerate_keyphrases(keywords, input_text)

        assert result == expected_results


    def test_regenerate_keyphrases__all_keywords(self):
        input_text = 'apple banana cherry'
        keywords = {'apple': 1, 'banana': 1, 'cherry': 1}
        expected_results = {'apple banana cherry':1}

        result = self.regenerate_keyphrases(keywords, input_text)

        assert result == expected_results


    def test_regenerate_keyphrases__multiple_keyphrases(self):
        input_text = 'apple banana cherry dog elephant fox grape horse iguana'
        keywords = {'apple': 1, 'banana': 1, 'dog': 2, 'elephant': 1, 'grape': 1, 'horse': 1}
        expected_results = {'apple banana':1, 'dog elephant':2, 'grape horse':1}

        result = self.regenerate_keyphrases(keywords, input_text)

        assert result == expected_results


    def test_regenerate_keyphrases__non_consecutive_keywords(self):
        """single word phrases are discarded, as we only want multiword phrases"""
        input_text = 'apple banana cherry dog elephant fox grape horse iguana'
        keywords = {'apple': 1, 'dog': 1, 'grape': 1}
        expected_results = {}

        result = self.regenerate_keyphrases(keywords, input_text)
        log.warning(result)

        assert result == expected_results


    def test_regenerate_keyphrases__keyphrase_at_end(self):
        input_text = 'apple banana cherry dog elephant fox grape horse iguana'
        keywords = {'grape': 1, 'horse': 1, 'iguana': 1}
        expected_results = {'grape horse iguana':1}

        result = self.regenerate_keyphrases(keywords, input_text)

        assert result == expected_results
        
    def test_regenerate_keyphrases__punctuation(self):
        input_text = "system of linear Diophantine equations, strict inequations"
        keywords = {'linear':1, 'Diophantine':2, 'equations':1}
        expected_results = {'linear diophantine equations': 2}
        
        result = self.regenerate_keyphrases(keywords, input_text)

        assert result == expected_results
        
    def test_example_from_train_data(self):
        input_text= "Stable feature selection via dense feature groups Many feature selection algorithms have been proposed in the past focusing on improving classification accuracy. In this work, we point out the importance of stable feature selection for knowledge discovery from high-dimensional data, and identify two causes of instability of feature selection algorithms: selection of a minimum subset without redundant features and small sample size. We propose a general framework for stable feature selection which emphasizes both good generalization and stability of feature selection results. The framework identifies dense feature groups based on kernel density estimation and treats features in each dense group as a coherent entity for feature selection. An efficient algorithm DRAGS (Dense Relevant Attribute Group Selector) is developed under this framework. We also introduce a general measure for assessing the stability of feature selection algorithms. Our empirical study based on microarray data verifies that dense feature groups remain stable under random sample hold out, and the DRAGS algorithm is effective in identifying a set of feature groups which exhibit both high classification accuracy and stability.\n"
        keywords = {'feature': 46, 'selection': 36, 'dense': 16, 'groups': 16, 'algorithms': 12}
        expected_results = {'feature selection': 46, 'dense feature groups': 46, 'feature selection algorithms': 46, 'feature selection algorithms selection': 46, 'feature groups': 46}
        result = self.regenerate_keyphrases(keywords, input_text)
        assert result == expected_results