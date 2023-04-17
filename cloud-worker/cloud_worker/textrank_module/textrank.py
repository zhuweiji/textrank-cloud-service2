import logging
import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Set, Union

import spacy
from spacy.tokens import Doc, Span

from .nlp import (
    _decode_unicode,
    _remove_non_ascii,
    _remove_non_core_words,
    _remove_stopwords,
    _simple_tokenize,
)
from .pagerank import Directed_Edge, Directed_Node, PageRank, Undirected_Node

"""
TextRank.keyword_extraction__undirected() - return a list of keywords from a string
"""

log = logging.getLogger(__name__)

@dataclass
class Keyword_Extraction_Result:
    nodes: List[Undirected_Node]


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    

class TextRank(metaclass=Singleton):
    def __init__(self) -> None:
        log.info('loading spacy model...')
        self.nlp = spacy.load('en_core_web_lg') # generate a spacy natural language processing object
    
    def sentence_extraction__undirected(self, text: Union[str, List[str]], iterations:int=100):
        if isinstance(text, str):
            text = _decode_unicode(text)
            text = _remove_non_ascii(text)
            nodes = [i.as_doc() for i in self.nlp(text).sents]
        
        elif isinstance(text, List):
            text = [_decode_unicode(i) for i in text]
            text = [_remove_non_ascii(i) for i in text]
            nodes = [self.nlp(i) for i in text]
            
        else: raise ValueError( f'expected str, instead got {type(text)}')
        
        nodes = self._generate_nodes_from_similarity(nodes)
        
        result = PageRank.calculate__undirected_no_optimise(nodes, iterations=iterations)
        
        sorted_result = sorted(result.items(), key=lambda x:x[1], reverse=True)
        result_nodes = []
        
        for node,score in sorted_result:
            # convert node to dict for serialization
                node_dict = node.asdict()
                node_dict['score'] = score
                result_nodes.append(node_dict)
                
        return result_nodes
        
    
    def keyword_extraction__undirected(self, string:str,
                                       iterations:int=100,
                                       number_to_keep: int=0,
                                       pos_tags:List[str] = ['NOUN','ADJ', 
                                                             'PROPN'
                                                            #  'VERB','ADV'
                                                             ],
                                       ):
        
        number_to_keep = number_to_keep or len(string) // 3 # as defined in the paper
        
        log.debug([(i.text, i.pos_) for i in self.nlp(string)])
        filtered_text = _decode_unicode(string)
        filtered_text = _remove_non_ascii(filtered_text)
        filtered_text = ' '.join([i.text for i in self.nlp(string) if i.pos_ in pos_tags])
        filtered_text = _remove_stopwords(filtered_text)
        filtered_text = _simple_tokenize(filtered_text)
        if not any(filtered_text): return []
        
        nodes = self._generate_nodes_from_cooccurence(filtered_text)
        result = PageRank.calculate__undirected_no_optimise(nodes, iterations=iterations)
        
        sorted_result = sorted(result.items(), key=lambda x:x[1], reverse=True)
        sorted_result = sorted_result[:number_to_keep]
        
        result_nodes: List[Dict[str,float]] = []
        
        for node,score in sorted_result:
            # convert node to dict for serialization
                node_dict = node.asdict()
                node_dict['score'] = score
                result_nodes.append(node_dict)
        return result_nodes
            
    def _generate_nodes_from_similarity(self, sentences:List[Doc], threshold: float = 0.5):
        node_dict = {}
        # helper function to get a Node from the dict or generate a new Node if one doesn't exist
        def get_from_node_dict(token_orth:str) -> Undirected_Node:
            if token_orth in node_dict: return node_dict[token_orth]
            else:
                node_dict[token_orth] = Undirected_Node(name=token_orth)
                return node_dict[token_orth]
        
        
        for idx, i in enumerate(sentences):
            i_node = get_from_node_dict(i.text)
            for jdx, j in enumerate(sentences[idx+1:]):
                j_node = get_from_node_dict(j.text)
                score = i.similarity(j)
                i_node.to(j_node, score)
        return list(node_dict.values())
    
    def _generate_nodes_from_cooccurence(self, tokens: List[str]) -> List[Undirected_Node]:
        """given a string, use coccurence to create an undirected graph where nodes are connected if they are coocurrent"""
        node_dict = {}
        
        # helper function to get a Node from the dict or generate a new Node if one doesn't exist
        def get_from_node_dict(token_orth:str):
            if token_orth in node_dict: return node_dict[token_orth]
            else:
                node_dict[token_orth] = Undirected_Node(name=token_orth)
                return node_dict[token_orth]
        
        
        for index,token in enumerate(tokens):
            node = get_from_node_dict(token)
            previous, next = self._find_cooccurent(tokens, index)
            nodes = [get_from_node_dict(token) for token in (*previous, *next)]
            for other_node in nodes:
                node.to(other_node)
                
        return list(node_dict.values())
        
    def regenerate_keyphrases(self, keyword_dict:Dict[str, int], original_text:str):
        """combine keywords that are next to each other"""
        keywords = set(i.lower() for i in keyword_dict)
        keyword_dict_copy = {k.lower():v for k,v in keyword_dict.items()}
        
        original_text = original_text.lower()
        split_text = self._tokenize(original_text)
        
        results:Dict[str, int] = {}
        keywords_used = set()
        
        # find keyphrases in the text by checking for contiguous keywords
        index = 0
        while index < len(split_text):
            token = split_text[index]
            
            if token not in keywords: 
                # the current word is not part of a keyphrase
                index+=1
                continue 
            
            keywords_used.add(token)
            max_score = keyword_dict_copy[token]
            keyphrase = [token]
            increment = 1
            
            while True:
                next_token = split_text[index+increment] if index+increment <= len(split_text)-1 else ''
                cleaned_next_token = re.sub(r'[^a-zA-Z0-9]', '', next_token)
                
                if not cleaned_next_token or cleaned_next_token not in keywords: # terminating condition - add phrase to results
                    results[' '.join(keyphrase)] = max_score
                    break
                
                score = keyword_dict_copy.get(cleaned_next_token) or keyword_dict_copy.get(next_token) or -1
                max_score = max(score, max_score)
                
                keywords_used.add(cleaned_next_token)
                keyphrase.append(cleaned_next_token)
                
                if (any(i in next_token for i in [',','.'])): # if the word has either comma or fullstop, then end the keyphrase
                    results[' '.join(keyphrase)] = max_score
                    break
                
                increment += 1
            
            index+=increment
            
        for i in keywords - keywords_used:
            results[i] = keyword_dict_copy[i] # add keywords that no keyphrases were found for
        
        # split phrases where there is a comma or fullstop in the text
        
        return results
            
            
            
            
            # if any(token in l for l in keywords) and index<len(tokenized_text)-1:
            #     next_token = tokenized_text[index+1]
            #     if any(next_token in l for l in keywords):
            #         pass
    
    def _tokenize(self, string:str):
        """tokenize text"""
        return _simple_tokenize(string)
    
    def _find_cooccurent(self, tokens:List[str], index, cooccurence_value:int=2):
        """returns the previous-n and next-n tokens 
        eg (0,1,2,3,4) with 2 as index returns ([0,1], (3,4))"""
        if isinstance(tokens, str): tokens = self._tokenize(tokens)
        return (tokens[index-cooccurence_value:index], tokens[index+1:index+2+1])
    
    
