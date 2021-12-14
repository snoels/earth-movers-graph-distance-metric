__author__ = "Sander Noels"

from pulp import *


def compute_graph_distance(graph1, graph2):
    """
    Computes the earth movers distance based graph distance between two graphs

    Parameters:
        graph1 (nx.Graph): source graph with weight values for every node
        graph2 (nx.Graph): sink graph with weight values for every node

    Returns:
       GraphDistance : distance information between two vertex-weighted trees
    """

    # tests
    if _sum_of_weights_not_equal_to_1(graph1) or _sum_of_weights_not_equal_to_1(graph2):
        raise ValueError("The sum of the vertex weights should be equal to 1.")

    if _equal_amount_of_nodes(graph1, graph2):
        raise ValueError("Graph 1 and graph 2 have a different amount of nodes.")

    # logic
    source_nodes = list(graph1.nodes)  # production nodes

    Fs = list(graph1.edges)
    Gs = list(graph1.edges)

    # we first create an LP problem
    prob = LpProblem("Earth_Movers_Distance_Based_Graph_Distance_Metric", LpMinimize)

    # all necessary variables are defined
    f_vars = LpVariable.dicts("F", Fs, cat="Continuous")
    g_vars = LpVariable.dicts("G", Gs, cat="Continuous")

    # The objective function
    prob += (
        lpSum([g_vars[(w, b)] for (w, b) in Gs]),
        "sum_of_the_weights_shifted_over_the_edges",
    )

    # flow constraint of a node
    for node in source_nodes:
        prob += lpSum(
            [
                _redirect_flows(j, node) * f_vars[(i, j)]
                for (i, j) in Fs
                if node in (i, j)
            ]
        ) == graph1.nodes[node]["weight"] - graph2.nodes[node][
            "weight"
        ], "sum_of_the_flows_of_a_node_%s" % (
            node
        )

    # absolute value constraints for a flow
    for (i, j) in Fs:
        prob += lpSum(g_vars[(i, j)]) >= f_vars[
            (i, j)
        ], "absolute_value_of_the_flow_%s" % (str(i) + "_" + str(j))
        prob += lpSum(g_vars[(i, j)]) >= -1 * f_vars[
            (i, j)
        ], "absolute_value_of_the_flow_%s" % (str(j) + "_" + str(i))

    if LpStatus[prob.solve()] != "Optimal":
        raise ValueError("The obtained solution is not optimal.")

    return GraphDistance(prob)


class GraphDistance:
    def __init__(self, prob):
        self._prob_variables = prob.variables()

    @property
    def total_abs_F(self):
        total_abs_F = 0

        for v in self._prob_variables:
            if v.name.startswith("G"):
                total_abs_F += v.varValue
        return total_abs_F

    @property
    def edges(self):
        if not hasattr(self, "_edges"):
            self.calculate_edges_and_values()
        return self._edges

    @property
    def values(self):
        if not hasattr(self, "_values"):
            self.calculate_edges_and_values()
        return self._values

    def calculate_edges_and_values(self):
        edges = []
        values = []

        for v in self._prob_variables:
            if v.name.startswith("F") and v.varValue != 0:
                start = v.name.find("(")
                end = v.name.find(")")

                tup = tuple(v.name[start + 1 : end].split(",_"))

                edges.append(tup)
                values.append(v.varValue)

        self._edges = [(int(i), int(j)) for i, j in edges]
        self._values = values


def _redirect_flows(j, node):
    """
    Assigns a negative value to an edge flow when j of (i,j) is equal to node
    """
    return -1 if node == j else 1


def _sum_of_weights_not_equal_to_1(graph):
    """
    Checks if the sum of the weighted nodes is equal to 1
    """
    sum_of_weights = round(
        sum([graph.nodes[node]["weight"] for node in graph.nodes]), 5
    )
    return sum_of_weights != 1


def _equal_amount_of_nodes(graph1, graph2):
    """
    Checks if the two graphs own the same nodes
    """
    return len(set(graph1.nodes).intersection(set(graph2.nodes))) != len(
        set(graph1.nodes)
    )
