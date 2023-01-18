__author__ = "Sander Noels"

import networkx as nx
from src.visualization.visualize import _get_filled_in_nodes, _get_nodes_to_save

def compute_graph_distance(graph_1, graph_2):
    graph_12 = _create_the_combined_difference_graph(graph_1, graph_2)
    graph_12 = _assign_root_distances(graph_12)

    max_distance = _get_max_distance_root(graph_12)
    queue = _get_nodes_from_distance(graph_12, max_distance)
    weights = []

    while max_distance > 1:
        while queue:
            node = queue.pop()
            node_weight = graph_12.nodes[node]['weight']
            parent = _get_parent(graph_12, node)
            graph_12.nodes[parent]['weight'] += node_weight
            weights.append(node_weight)
        max_distance -= 1
        queue = _get_nodes_from_distance(graph_12, max_distance)

    return sum([abs(w) for w in weights])



def _create_the_combined_difference_graph(graph_1, graph_2):

    nw = graph_1.copy()

    # assign weight differences to nodes
    weight_differences = {node : {'weight' : graph_1.nodes[node]['weight'] - graph_2.nodes[node]['weight']} for node in graph_1.nodes}
    nx.set_node_attributes(nw, weight_differences)

    filled_in_nodes_1 = _get_filled_in_nodes(graph_1)
    filled_in_nodes_2 = _get_filled_in_nodes(graph_2)
    filled_in_combined = filled_in_nodes_1.union(filled_in_nodes_2)

    nodes_to_save = _get_nodes_to_save(filled_in_combined, nw)
    nodes_to_remove = set(graph_1.nodes).difference(set(nodes_to_save))
    nw.remove_nodes_from(nodes_to_remove)

    return nw


def _get_parent(graph, node):
    return list(graph.predecessors(node))[0]

def _get_distance_from_root(nw, node, root):
    distance = len(nx.shortest_path(nw, node, root))
    return distance

def _assign_root_distances(graph):
    nw = graph.copy()
    for node in graph.nodes:
        nw.nodes[node]['distance_to_root'] = _get_distance_from_root(graph, 0, node)
    return nw

def _get_max_distance_root(nw):
    return max([nw.nodes[node]['distance_to_root'] for node in nw.nodes])

def _get_nodes_from_distance(graph, distance):
    return set([node for node in graph.nodes() if graph.nodes[node]['distance_to_root'] == distance])