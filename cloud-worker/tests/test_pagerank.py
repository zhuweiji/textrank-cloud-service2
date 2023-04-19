import logging

import pytest

from cloud_worker.textrank_module.pagerank import PageRank, Undirected_Node

log = logging.getLogger(__name__)

class TestPagerank:
    def test_convert_to_matrix(self):
        node_a = Undirected_Node(name='Yahoo')
        node_b = Undirected_Node(name='Amazon')
        node_c = Undirected_Node(name='Microsoft')
        node_a.to(node_a)
        node_a.to(node_b)
        node_b.to(node_c)
        nodes = [node_a, node_b, node_c]
        result = PageRank.convert_connected_nodes_to_matrix(nodes)
        
        assert result == [[1, 1, 0], [1, 0, 1], [0, 1, 0]]
        
    def test_lecture_example(self):
        node_a = Undirected_Node(name='Yahoo')
        node_b = Undirected_Node(name='Amazon')
        node_c = Undirected_Node(name='Microsoft')
        node_a.to(node_a, )
        node_a.to(node_b)
        node_b.to(node_c)
        nodes = [node_a, node_b, node_c]
        result = PageRank.calculate__undirected_no_optimise(nodes)
        
        log.error(result)
        assert False
    
    def test_empty_graph(self):
        nodes = []
        result = PageRank.calculate__undirected_no_optimise(nodes)
        assert result == {}
        
    def test_single_node_graph(self):
        node = Undirected_Node(name='A')
        nodes = [node]
        result = PageRank.calculate__undirected_no_optimise(nodes)
        assert result == {node: 1.0}
        
    def test_two_node_graph(self):
        node_a = Undirected_Node(name='A')
        node_b = Undirected_Node(name='B')
        node_a.to(node_b)
        log.warning(node_a.connected)
        nodes = [node_a, node_b]
        result = PageRank.calculate__undirected_no_optimise(nodes)
        
        assert len(result) == 2
        assert abs(result[node_a] - 1.0) < 0.001
        assert abs(result[node_b] - 1.0) < 0.001

    def test_multi_node_graph(self):
        node_a = Undirected_Node(name='A')
        node_b = Undirected_Node(name='B')
        node_c = Undirected_Node(name='C')
        node_d = Undirected_Node(name='D')
        node_e = Undirected_Node(name='E')
        node_a.to(node_b)
        node_a.to(node_c)
        node_b.to(node_c)
        node_c.to(node_d)
        node_e.to(node_a)
        node_e.to(node_b)
        nodes = [node_a, node_b, node_c, node_d, node_e]
        result = PageRank.calculate__undirected_no_optimise(nodes)
        
        log.error(result)
        assert len(result) == 5
        assert abs(result[node_a] - 0.2830) < 0.001
        assert abs(result[node_b] - 0.3283) < 0.001
        assert abs(result[node_c] - 0.2653) < 0.001
        assert abs(result[node_d] - 0.0652) < 0.001
        assert abs(result[node_e] - 0.0582) < 0.001
