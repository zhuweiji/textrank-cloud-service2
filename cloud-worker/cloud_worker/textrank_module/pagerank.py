from __future__ import annotations

import logging
import random
from dataclasses import asdict, dataclass, field
from itertools import count
from typing import Any, List, Tuple, Union

from numpy import transpose

from cloud_worker.textrank_module.pagerank_wt import iterative_pr, noniterative_pr

log = logging.getLogger(__name__)


@dataclass
class Undirected_Node:
    id:         int = field(default_factory=count().__next__, init=False)
    name:       str = ''
    connected:  set[Undirected_Edge] = field(default_factory=lambda: set(), repr=False)
    
    def to(self, other: Undirected_Node, weight:Union[int, float]=1):
        e = Undirected_Edge(self, other, weight)
        self.connected.add(e)
        if other is not self:
            other.connected.add(e)
        
        
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __repr__(self) -> str:
        return f'Undirected Node {self.name}: {[i.get_other(self).name for i in self.connected]}'
    
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
        return hash(f"{self.first}-{self.second}|{self.second}-{self.first}")


        
class PageRank:
    @classmethod
    def convert_connected_nodes_to_matrix(cls, nodes: List[Undirected_Node]):
        M = [[0.0 for j in range(len(nodes))] for i in range(len(nodes))]
        # ordered_nodes = sorted(nodes, key=lambda x: x.id)
        
        for col,node in enumerate(nodes):
            connected_nodes = {edge.get_other(node): edge.weight for edge in node.connected}
            for row, other in enumerate(nodes):
                weight = connected_nodes.get(other, 0)
                M[row][col] = weight
                
        def normalization(arr):
            ans = []
            for row in arr:
                row_sum = sum(row)
                if row_sum != 1:
                    curr = []
                    for num in row:
                        curr.append(num/(row_sum ))
                    ans.append(curr)
                else:
                    ans.append(row)
            return ans
        log.warning(M)
        M = normalization(M)
        M = transpose(M).tolist()
        log.warning(M)
        
        return M
    
        
                
    
    @classmethod
    def calculate__undirected_no_optimise(cls, nodes: List[Undirected_Node], iterations:int = 20, random_surf_prob:float=0.1, convergence_threshold=0.001):
        """Calculate scores for nodes given a list of nodes which are connected via directionless connection (a undirected graph)"""
        M = cls.convert_connected_nodes_to_matrix(nodes)
        log.warning(M)
        scores = iterative_pr(M, 1-random_surf_prob, iterations)
        log.warning([i/min(scores) for i in scores])
        log.warning(scores)
        return {k:v for k,v in zip(nodes, scores)}
        # node_scores = {i:1.0 for i in nodes}
        
        # previous_total_score = None
        # complete = False
        
        # while not complete:
        #     current_total_score = 0
        #     node_scores_this_iteration = {k:v for k,v in node_scores.items()} # keep a dict to hold the new scores of the nodes, but only update at the end 
            
        #     for node in nodes:
        #         node_score = 0 if node.connected else 1
        #         for i in node.connected: 
        #             # add random surfer probability here to mitigate dead end nodes
        #             if random.random() - random_surf_prob <= 0:
        #                 random_node = random.choice(nodes)
        #                 if random_node.connected: i = random.choice(tuple(random_node.connected))

        #             edge_weight = node_scores[i.get_other(node)]
        #             node_score += edge_weight 
        #             log.warning(f'{node.name} {i.get_other(node).name} {edge_weight / len(i.get_other(node).connected)}' )
        #             # node_score += edge_weight 
                    
        #         node_scores_this_iteration[node] = node_score / len(nodes)
        #         current_total_score += node_score
                
        #     node_scores = node_scores_this_iteration
            
        #     if previous_total_score:
        #         log.warning(current_total_score - previous_total_score)
        #     log.error({k.name: v for k,v in node_scores.items()})
            
        #     if previous_total_score and abs(current_total_score - previous_total_score) <= convergence_threshold:
        #         complete = True
        #     previous_total_score = current_total_score
        #     iterations -= 1
        #     if iterations <= 1: complete = True
            
        #     log.debug(f'iterations={iterations}')        
            
        # return node_scores
            
            
        
    @classmethod
    def calculate__directed_no_optimise(cls, nodes: List['Directed_Node'], iterations:int = 10):
        raise NotImplementedError
    #     """Calculate scores for nodes given a list of nodes which are connected via one-way connections (a directed graph)"""
    #     node_scores = {i:1 for i in nodes}
        
    #     complete = False
    #     current_total_score = None
        
    #     while not complete:
    #         current_total_score = 0
    #         for node in nodes:
    #             node_score =  sum(i.weight for i in node.in_set)
    #             node_scores[node] = node_score
                
    #             current_total_score += node_score
            
    #         iterations -= 1
    #         if iterations <= 1: complete = True
            
    #     log.debug(f'iterations={iterations}')        
    #     return node_scores

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