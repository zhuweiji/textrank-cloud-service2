from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from itertools import count
from threading import current_thread
from typing import List

logging.basicConfig(format='%(name)s-%(levelname)s|%(lineno)d:  %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

@dataclass
class Undirected_Node:
    id:         int = field(default_factory=count().__next__, init=False)
    name:       str = ''
    connected:  set = field(default_factory=lambda: set(), repr=False)
    
    def to(self, other: Undirected_Node):
        self.connected.add(other)
        other.connected.add(self)
        
    def __hash__(self) -> int:
        return hash(self.id)
    
    def full_str(self):
        return f"Undirected Node {self.name}: {self.connected}"

@dataclass
class Directed_Node:
    id:      int = field(default_factory=count().__next__, init=False)
    name:    str = ''
    in_set:  set = field(default_factory=lambda: set(), repr=False)
    out_set: set = field(default_factory=lambda: set(), repr=False)
    
    def to(self, other: Directed_Node):
        self.out_set.add(other)
        other.in_set.add(self)
        
    def __hash__(self) -> int:
        return hash(self.id)
    
    
class PageRank:
    @classmethod
    def calculate__undirected_no_optimse(self, nodes: List[Undirected_Node], convergence_threshold: float = None, iterations:int = 10):
        if convergence_threshold and iterations: raise ValueError('cannot have both args at once')
        
        node_scores = {i:1 for i in nodes}
        
        current_total_score = None
        iterations = iterations or 0
        
        complete = False
        
        while not complete:
            previous_total_score = current_total_score or 0 
            current_total_score = 0
            
            marked = set()
            for node in nodes:
                if node in marked: continue
                for i in node.connected: marked.add(i)
                node_score = sum(node_scores[i] for i in node.connected)
                
                node_scores[node] = node_score
                current_total_score += node_score
                
            if convergence_threshold:
                if current_total_score - previous_total_score < convergence_threshold: complete = True
                iterations += 1
            elif iterations:
                iterations -= 1
                if iterations <= 1: complete = True
            log.debug(f'iterations={iterations}')        
            
        return node_scores
            
            
        
    @classmethod
    def calculate__directed_no_optimise(cls, nodes: List[Directed_Node], convergence_threshold: float, iterations:int = 10):
        if convergence_threshold and iterations: raise ValueError('cannot have both args at once')
        
        node_scores = {i:1 for i in nodes}
        
        complete = False
        current_total_score = None
        
        iterations = iterations or 0
        while not complete:
            previous_total_score = current_total_score or 0 
                
            current_total_score = 0
            for node in nodes:
                node_score =  sum(node_scores[i] for i in node.in_set)
                node_scores[node] = node_score
                
                current_total_score += node_score
            
            if convergence_threshold:
                if current_total_score - previous_total_score < convergence_threshold: complete = True
                iterations += 1
            elif iterations:
                iterations -= 1
                if iterations <= 1: complete = True
            
        log.debug(f'iterations={iterations}')        
        return node_scores
            

# class PageRankTestBench:
#     @staticmethod
#     def setup__directed(NUM_NODES: int, NUM_EDGES: int):
#         nodes = [Directed_Node() for i in range(NUM_NODES)]
#         for _ in range(NUM_EDGES):
#             from_node = random.choice(nodes)
#             to_node = random.choice(nodes)
#             from_node.to(to_node)         
        
#         return nodes   
                
#     @staticmethod
#     def setup__undirected(NUM_NODES: int, NUM_EDGES: int):
#         nodes = [Undirected_Node() for i in range(NUM_NODES)]
#         for _ in range(NUM_EDGES):
#             from_node = random.choice(nodes)
#             to_node = random.choice(nodes)
#             from_node.to(to_node)         
        
#         return nodes   

# if __name__ == "__main__":
#     NUM_NODES = 250
#     NUM_EDGES = 250
    
#     nodes = PageRankTestBench.setup(NUM_NODES=1000, NUM_EDGES=1000)
#     node_scores = PageRank.calculate__undirected_no_optimse(nodes=nodes, convergence_threshold=2)
    
#     filtered = {k.id: v
#         for k,v in node_scores.items()
#     }
#     node_scores_sorted = sorted(filtered.items(), key=lambda x:x[1], reverse=True)
    
#     log.info(node_scores_sorted[:5])
#     log.info(node_scores_sorted[-5:])
    
    