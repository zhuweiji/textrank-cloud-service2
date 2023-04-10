from __future__ import annotations

import logging
import random
from dataclasses import asdict, dataclass, field
from itertools import count
from operator import itemgetter
from threading import current_thread
from typing import Any, List, Tuple, Union

log = logging.getLogger(__name__)


@dataclass
class Undirected_Node:
    id:         int = field(default_factory=count().__next__, init=False)
    name:       str = ''
    connected:  set[Undirected_Edge] = field(default_factory=lambda: set(), repr=False)
    
    def to(self, other: Undirected_Node, weight:Union[int, float]=1):
        self.connected.add(Undirected_Edge(self, other, weight))
        
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __repr__(self) -> str:
        return f'Undirected Node {self.id}: {[i.get_other(self).id for i in self.connected]}'
    
    def __eq__(self, __value: Undirected_Node) -> bool:
        return self.id == __value.id
    
    def full_str(self):
        return f"Undirected Node {self.name}: {self.connected}"
    
    def asdict(self):
        class_attributes = [attr for attr in dir(self) 
                            if '__' not in attr and not callable(getattr(self, attr))
                            and attr != 'connected']
        
        # class_attributes = ['id','name']
        
        self_asdict = {attr: getattr(self, attr) for attr in class_attributes}
        self_asdict['connected'] = [i.get_other(self).id for i in self.connected]
        return self_asdict

@dataclass
class Undirected_Edge:
    first : Undirected_Node
    second: Undirected_Node
    
    weight: Union[int,float] = 1
    
    def get_other(self, other_node: Undirected_Node):
        return self.second if self.first == other_node else self.first
    
    def __hash__(self) -> int:
        return hash(f"{self.first}-{self.second}")

@dataclass
class Directed_Node:
    id:      int = field(default_factory=count().__next__, init=False)
    name:    str = ''
    in_set:  set[Directed_Edge] = field(default_factory=lambda: set(), repr=False)
    out_set: set[Directed_Edge] = field(default_factory=lambda: set(), repr=False)
    
    def to_node(self, other: Directed_Node, weight=1):
        edge = Directed_Edge(from_node=self, to_node=other, weight=weight)
        self.out_set.add(edge)
        other.in_set.add(edge)
        
    def from_node(self, other: Directed_Node, weight=1):
        edge = Directed_Edge(from_node=other, to_node=self, weight=weight)
        self.in_set.add(edge)
        other.out_set.add(edge)
        
    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class Directed_Edge:
    from_node: Directed_Node
    to_node  : Directed_Node
    weight: int = 1
        
class PageRank:
    
    @classmethod
    def calculate__undirected_no_optimise(cls, nodes: List[Undirected_Node], iterations:int = 10, random_surf_prob:float=0.1):
        """Calculate scores for nodes given a list of nodes which are connected via directionless connection (a undirected graph)"""
        
        node_scores = {i:1.0 for i in nodes}
        
        current_total_score = None
        complete = False
        
        while not complete:
            current_total_score = 0
            
            for node in nodes:
                node_score = 0
                for i in node.connected: 
                    # add random surfer probability here to mitigate dead end nodes
                    if random.random() - random_surf_prob <= 0:
                        random_node = random.choice(nodes)
                        if random_node.connected:
                            i = random.choice(tuple(random_node.connected))
                    
                    edge_weight = i.weight
                    node_score += edge_weight
                
                node_scores[node] = node_score
                current_total_score += node_score
                
            iterations -= 1
            if iterations <= 1: complete = True
            log.debug(f'iterations={iterations}')        
            
        return node_scores
            
            
        
    @classmethod
    def calculate__directed_no_optimise(cls, nodes: List[Directed_Node], iterations:int = 10):
        """Calculate scores for nodes given a list of nodes which are connected via one-way connections (a directed graph)"""
        node_scores = {i:1 for i in nodes}
        
        complete = False
        current_total_score = None
        
        while not complete:
            current_total_score = 0
            for node in nodes:
                node_score =  sum(i.weight for i in node.in_set)
                node_scores[node] = node_score
                
                current_total_score += node_score
            
            iterations -= 1
            if iterations <= 1: complete = True
            
        log.debug(f'iterations={iterations}')        
        return node_scores
                