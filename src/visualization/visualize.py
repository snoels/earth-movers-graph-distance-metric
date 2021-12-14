__author__ = "Sander Noels"

import matplotlib.pyplot as plt
import networkx as nx


def visualize_company(graph, digits):

    nw = graph.copy()

    weighted_vertices = [node for node in nw.nodes if nw.nodes[node]["weight"] != 0]
    nodes_to_remove = _nodes_to_remove(nw, weighted_vertices)
    nw.remove_nodes_from(nodes_to_remove)

    plt.figure(figsize=(14, 7))
    labels = nx.get_node_attributes(nw, "weight")
    labels = {k: str(k) + " : " + str(round(v, digits)) for k, v in labels.items()}
    nx.draw(
        nw,
        edge_color="red",
        pos=nx.drawing.nx_agraph.graphviz_layout(nw, prog="dot"),
        labels=labels,
        with_labels=True,
        font_size=14,
    )
    plt.show()


def plot_edge_flows(graph_1, graph_2, edges, flows, digits):

    nw = _create_the_combined_graph(graph_1, graph_2)
    edge_labels = _create_edge_labels(nw, edges, flows, digits)

    plt.figure(figsize=(12, 8))
    nx.draw(
        nw,
        edge_color="red",
        pos=nx.drawing.nx_agraph.graphviz_layout(nw, prog="dot"),
        with_labels=True,
    )
    nx.draw_networkx_edge_labels(
        nw,
        pos=nx.drawing.nx_agraph.graphviz_layout(nw, prog="dot"),
        edge_labels=edge_labels,
    )
    plt.show()


def _nodes_to_remove(nw, weighted_vertices):
    nodes_to_keep = _nodes_to_keep(nw, weighted_vertices)
    return set(nw.nodes()).difference(set(nodes_to_keep))


def _nodes_to_keep(nw, weighted_vertices):
    nodes_to_keep = []
    for node in nw.nodes:
        if node in weighted_vertices:
            # 0 is the root
            nodes_to_keep += nx.shortest_path(nw, 0, node)
    return nodes_to_keep


def _create_the_combined_graph(graph_1, graph_2):

    nw = graph_1.copy()

    filled_in_nodes_1 = _get_filled_in_nodes(graph_1)
    filled_in_nodes_2 = _get_filled_in_nodes(graph_2)
    filled_in_combined = filled_in_nodes_1.union(filled_in_nodes_2)

    nodes_to_save = _get_nodes_to_save(filled_in_combined, nw)
    nodes_to_remove = set(graph_1.nodes).difference(set(nodes_to_save))
    nw.remove_nodes_from(nodes_to_remove)

    return nw


def _get_filled_in_nodes(graph):
    return set([node for node in graph.nodes if graph.nodes[node]["weight"] != 0])


def _get_nodes_to_save(filled_in_combined, nw):
    nodes_to_save = []
    for node in filled_in_combined:
        nodes_to_save += nx.shortest_path(nw, 0, node)
    return nodes_to_save


def _create_edge_labels(nw, edges, values, digits):

    edge_labels = []

    for edge in nw.edges:
        if edge in edges:
            idx = edges.index(edge)
            if abs(values[idx]) > 0:
                edge_labels.append(str(round(values[idx], digits)))
            else:
                edge_labels.append("")
        else:
            edge_labels.append("")

    return {edge: label for edge, label in zip(nw.edges, edge_labels)}
