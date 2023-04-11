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
        other.connected.add(Undirected_Edge(other, self, weight))
        
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
    def calculate__undirected_no_optimise(cls, nodes: List[Undirected_Node], convergence_threshold:int = 5,
                                          iterations:int = 10, random_surf_prob:float=0.1):
        """Calculate scores for nodes given a list of nodes which are connected via directionless connection (a undirected graph)
        nodes:            A list of undirected nodes to run pagerank on
        iterations:       Number of iterations to run the algorithm before stopping
        random_surf_prob: The probability that a user moves to a random node instead of the next adjacent node
        """
        
        def find_random_edge():
            chosen_edge = None
            while not chosen_edge:
                random_node = random.choice(nodes)
                if random_node.connected: return random.choice(tuple(random_node.connected))
        
        node_scores = {i:1.0 for i in nodes}
        
        # if there 
        if not any(i.connected for i in nodes): return node_scores
        
        complete = False
        
        while not complete:
            total_score = len(nodes) # keep a counter to track the total score of all nodes in the graph, 
            new_edge_weights = {}
            
            for node in nodes:
                node_score = 0
                
                for connected_edge in node.connected: 
                    # add random probability to move to a random edge
                    edge = connected_edge if not random.random() - random_surf_prob > 0 else find_random_edge() 
                    
                    # this condition is because the typechecker says find_random_edge may return None
                    # but this will never happen because we have guranteed that there is at least one edge in the graph
                    if not edge: raise ValueError 
                    
                    # add the normalized weight of the edge 
                    edge_weight = edge.weight  / len(edge.get_other(node).connected)
                    node_score += edge_weight
                    
                    # save the new score for the node, but only update the scores of all nodes after all nodes have been computed
                    new_edge_weights[node] = node_score
                
            # update the scores of all nodes                    
            for (node,score) in new_edge_weights.items():
                node_scores[node] = score 
                
            # total change in the values of all edges after this iteration
            new_score = sum(new_edge_weights.values())
            if abs(total_score - new_score) < convergence_threshold: complete = True
            total_score = new_score 
                
            iterations -= 1
            if iterations <= 1: complete = True
            log.debug(f'iterations={iterations}')        
            
        return node_scores
            
            
        
    @classmethod
    def calculate__directed_no_optimise(cls, nodes: List[Directed_Node], iterations:int = 10):
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

if __name__ == "__main__":
    nodes = [
        Undirected_Node('1'),
        Undirected_Node('2'),
        Undirected_Node('3'),
        Undirected_Node('4'),
        Undirected_Node('5'),
        Undirected_Node('6'),
    ]
    
    node1,node2,node3,node4,node5,node6 = nodes
    node1.to(node2)
    node1.to(node3)
    node1.to(node6)
    node2.to(node4)
    node2.to(node5)
    node2.to(node6)
    print(PageRank.calculate__undirected_no_optimise(nodes, iterations=20))
    