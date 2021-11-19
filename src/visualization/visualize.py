__author__ = 'Sander Noels'

from networkx.drawing.nx_pydot import graphviz_layout #TODO @SN unused param?
import matplotlib.pyplot as plt
import networkx as nx


def visualize_company(graph):
    
    nw = graph.copy()
        
    weighted_vertices = [node for node in nw.nodes if nw.nodes[node]['weight'] != 0]

    # TODO @SN Split this of in a private function?
    nodes_to_remove = _notes_to_remove(nw, weighted_vertices)
    nw.remove_nodes_from(nodes_to_remove)
    
    plt.figure(figsize=(14, 7))
    labels = nx.get_node_attributes(nw, 'weight') 
    labels = {k: str(k) + ' : ' + str(round(v, 3)) for k, v in labels.items()} 

    nx.draw(nw,
            edge_color='red',
            pos=nx.drawing.nx_agraph.graphviz_layout(nw, prog='dot'),
            labels=labels,
            with_labels=True,
            font_size=14)

    plt.show()


def _notes_to_remove(nw, weighted_vertices):
    nodes_to_keep = _nodes_to_keep(nw, weighted_vertices)
    return set(nw.nodes()).difference(set(nodes_to_keep))


def _nodes_to_keep(nw, weighted_vertices):
    nodes_to_keep = []
    for node in nw.nodes:
        if node in weighted_vertices:
            # 0 is the root
            nodes_to_keep += nx.shortest_path(nw, 0, node)
    return nodes_to_keep


#TODO @SN I would make this private _create_the_combined_graph and put it below the public
def create_the_combined_graph(graph_1, graph_2):

    nw = graph_1.copy()

    #todo @SN code duplication split of eg: get_all_non_top_nodes(graph1)
    filled_in_nodes_1 = set([node for node in graph_1.nodes if graph_1.nodes[node]['weight'] != 0])
    filled_in_nodes_2 = set([node for node in graph_2.nodes if graph_2.nodes[node]['weight'] != 0])

    filled_in_combined = filled_in_nodes_1.union(filled_in_nodes_2)

    #TODO @SN you can split this one
    nodes_to_save = _get_notes_to_save(filled_in_combined, nw)

    for node in graph_1.nodes:
        if node not in nodes_to_save:
            nw.remove_node(node)
    return nw


def _get_notes_to_save(filled_in_combined, nw):
    nodes_to_save = []
    for node in filled_in_combined:
        nodes_to_save += nx.shortest_path(nw, 0, node)
    return nodes_to_save


def create_edge_labels(nw, edges, values):

    edge_labels = []

    for edge in nw.edges:
        if edge in edges:
            idx = edges.index(edge)
            if abs(values[idx]) > 0:
                edge_labels.append(str(round(values[idx], 4))) #TODO @SN any perticular reason
                # why 4? if so maybe make it a constant
            else:
                edge_labels.append('')
        else:
            edge_labels.append('')
            
    return {edge: label for edge, label in zip(nw.edges, edge_labels)}

def plot_edge_flows(graph_1, graph_2, edges, flows):
    
    nw = create_the_combined_graph(graph_1,graph_2)
    
    edge_labels = create_edge_labels(nw, edges,flows)
    
    plt.figure(figsize = (12,8))
    nx.draw(nw, edge_color='red', pos=nx.drawing.nx_agraph.graphviz_layout(nw, prog='dot'), with_labels=True )
    nx.draw_networkx_edge_labels(nw,pos=nx.drawing.nx_agraph.graphviz_layout(nw, prog='dot'),edge_labels=edge_labels)
    plt.show()