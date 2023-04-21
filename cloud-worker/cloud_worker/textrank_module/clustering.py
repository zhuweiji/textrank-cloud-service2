import logging
from typing import Dict, List, Set

import networkx as nx
import numpy as np
from spacy.tokens import Doc, Span

from cloud_worker.textrank_module.pagerank import Undirected_Node

log = logging.getLogger(__name__)

def cluster_sentences(nodes: List[Undirected_Node]) -> List[Set[str]]:
        edge_75_percentile = np.percentile(
            [[edge.weight] for node in nodes for edge in node.connected],
            75)
        n = {node.id: [i.get_other(node).id for i in node.connected if i.weight > edge_75_percentile] for node in nodes}
        
        g = nx.Graph(n)
        return [i for i in nx.connected_components(g)]