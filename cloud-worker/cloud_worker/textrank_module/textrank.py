import logging
from dataclasses import asdict, dataclass
from typing import List, Union

import spacy
from spacy.tokens import Doc, Span

from .nlp import (
    _decode_unicode,
    _remove_non_ascii,
    _remove_non_core_words,
    _remove_stopwords,
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
        
    
    def keyword_extraction__undirected(self, string:str, iterations:int=100, remove_stopwords:bool=True):
        if remove_stopwords: string = _remove_stopwords(string)
        nodes = self._generate_nodes_from_cooccurence(string)
        result = PageRank.calculate__undirected_no_optimise(nodes, iterations=iterations)
        
        sorted_result = sorted(result.items(), key=lambda x:x[1], reverse=True)
        result_nodes = []
        
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
    
    def _generate_nodes_from_cooccurence(self, string: str) -> List[Undirected_Node]:
        """given a string, use coccurence to create an undirected graph where nodes are connected if they are coocurrent"""
        tokens = self._tokenize(string)
        # node_dict = keydefaultdict(default_factory=lambda token_orth: Undirected_Node(name=token_orth))
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
        
    # @classmethod
    # def collapse_keywords(cls, keywords:List[str], text:str):
    # combine keywords that are next to each other
    #     keyphrases = set([i] for i in keywords)
        
    #     tokenized_text = cls.tokenize(text)
    #     for index,token in enumerate(tokenized_text):
    #         if any(token in l for l in keyphrases) and index<len(tokenized_text)-1:
    #             next_token = tokenized_text[index+1]
    #             if any(next_token in l for l in keyphrases):
    
    @staticmethod
    def _tokenize(string:str):
        """tokenize text"""
        # honestly there are more correct ways to tokenize strings (but this is sufficient for us)
        return string.split()
    
    def _find_cooccurent(self, tokens:List[str], index, cooccurence_value:int=2):
        """returns the previous-n and next-n tokens 
        eg (0,1,2,3,4) with 2 as index returns ([0,1], (3,4))"""
        if isinstance(tokens, str): tokens = self._tokenize(tokens)
        return (tokens[index-cooccurence_value:index], tokens[index+1:index+2+1])
    
    
