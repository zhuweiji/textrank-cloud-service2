import logging
from dataclasses import dataclass
from typing import List

from .nlp import remove_stopwords as _remove_stopwords
from .pagerank import PageRank, Undirected_Node

"""
TextRank.keyword_extraction__undirected() - return a list of keywords from a string
"""

log = logging.getLogger(__name__)

@dataclass
class TextRankKeywordResult:
    text: str
    score: int
    
    def __repr__(self) -> str:
        return f'text: {self.text} | score: {self.score}'

class TextRank:
    @classmethod
    def keyword_extraction__undirected(cls, string:str, iterations:int=50, remove_stopwords:bool=True, min_score: int=2):
        if remove_stopwords: string = _remove_stopwords(string)
        nodes = cls._generate_nodes_from_cooccurence(string)
        result = PageRank.calculate__undirected_no_optimse(nodes, iterations=iterations)
        sorted_result = sorted(result.items(), key=lambda x:x[1], reverse=True)
        
        
        return [TextRankKeywordResult(text=i[0].name, score=i[1]) for i in sorted_result if i[1] > min_score]
    
    # @classmethod
    # def collapse_keywords(cls, keywords:List[str], text:str):
    #     keyphrases = set([i] for i in keywords)
        
    #     tokenized_text = cls.tokenize(text)
    #     for index,token in enumerate(tokenized_text):
    #         if any(token in l for l in keyphrases) and index<len(tokenized_text)-1:
    #             next_token = tokenized_text[index+1]
    #             if any(next_token in l for l in keyphrases):
                    
    
    @classmethod
    def _generate_nodes_from_cooccurence(cls, string: str):
        tokens = cls._tokenize(string)
        # node_dict = keydefaultdict(default_factory=lambda token_orth: Undirected_Node(name=token_orth))
        node_dict = {}
        
        def get_from_node_dict(token_orth:str):
            if token_orth in node_dict: return node_dict[token_orth]
            else:
                node_dict[token_orth] = Undirected_Node(name=token_orth)
                return node_dict[token_orth]
        
        
        for index,token in enumerate(tokens):
            node = get_from_node_dict(token)
            previous, next = cls._find_cooccurent(tokens, index)
            nodes = [get_from_node_dict(token) for token in (*previous, *next)]
            for other_node in nodes:
                node.to(other_node)
                
        return list(node_dict.values())
        
    @staticmethod
    def _tokenize(string:str):
        # honestly there are more correct ways to tokenize strings (but this is sufficient for us)
        return string.split()
    
    @classmethod
    def _find_cooccurent(cls, tokens:List[str], index, cooccurence_value:int=2):
        if isinstance(tokens, str): tokens = cls._tokenize(tokens)
        return (tokens[index-cooccurence_value:index], tokens[index+1:index+2+1])
    