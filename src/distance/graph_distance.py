__author__ = 'Sander Noels'

from pulp import *

#TODO @SN you might want to make this "private" -> _redirect_flows(...)
# also as this is merely a helper function i would put it below the more interesting one
def redirect_flows(j, node):
    """
    Assigns a negative value to an edge flow when j of (i,j) is equal to node

    Params:
    node(str): node name of the node where the in-and outgoing flows are calculated for
    j(str): node name
    """
    #TODO @SN shorten it? return 1 if node == j else 1
    if node == j:
        return -1
    else:
        return 1

def compute_graph_distance(graph1, graph2, edge_flows=False):
    """
    Computes the earth-movers distance based graph distance between two graphs

    Params:
    graph1(nx.Graph): source graph with weight values for every node
    graph2(nx.Graph): sink graph with weight values for every node
    #TODO @SN if you keep the flag(see below) you have to document it.
    """

    # tests
    #TODO @SN put this in a function eg if _sum_of_vertexes_not_equal_to_1(graph1):
    if round(sum([graph1.nodes[node]["weight"] for node in graph1.nodes]), 5) != 1 or \
            round(sum([graph2.nodes[node]["weight"] for node in graph2.nodes]), 5) != 1:
        raise ValueError('The sum of the vertex weights should be equal to 1.')

    #TODO @SN same here eg if not equal_amount_of_nodes(graph1,graph2):
    if len(set(graph1.nodes).intersection(set(graph2.nodes))) != len(set(graph1.nodes)):
        raise ValueError('Graph 1 and graph 2 have a different amount of nodes.')

    source_nodes = list(graph1.nodes)  # production nodes

    sink_nodes = list(graph2.nodes)  # consumption nodes #TODO @SN not used?

    # graph1 and graph2 are equal we can use the edges of both graphs
    Fs = list(graph1.edges)
    Gs = list(graph1.edges)

    # we first create an LP problem
    prob = LpProblem("Earth_Movers_Distance_Based_Graph_Distance_Metric", LpMinimize)

    # all necessary variables are defined
    f_vars = LpVariable.dicts("F", Fs, cat='Continuous')
    g_vars = LpVariable.dicts("G", Gs, cat='Continuous')

    # The objective function
    prob += lpSum([g_vars[(w, b)] for (w, b) in Gs]), "sum_of_the_weights_shifted_over_the_edges"

    # flow constraint of a node
    for node in source_nodes:
        #TODO @SN feels like you meight want to write this in full to make it more readable
        # you might lose some performance without list comp though
        prob += lpSum(
            [redirect_flows(j, node) * f_vars[(i, j)] for (i, j) in Fs if node in (i, j)]) == \
                graph1.nodes[node]["weight"] - graph2.nodes[node][
                    "weight"], "sum_of_the_flows_of_a_node_%s" % (node)

    # absolute value constraints for a flow
    for (i, j) in Fs:
        prob += lpSum(g_vars[(i, j)]) >= f_vars[(i, j)], "absolute_value_of_the_flow_%s" % (
                str(i) + '_' + str(j))
        prob += lpSum(g_vars[(i, j)]) >= -1 * f_vars[(i, j)], "absolute_value_of_the_flow_%s" % (
                str(j) + '_' + str(i))

    if LpStatus[prob.solve()] != 'Optimal':
        raise ValueError('The obtained solution is not optimal.')

    total_abs_F = 0

    for v in prob.variables():
        if v.name.startswith('G'):
            total_abs_F += v.varValue

    if edge_flows == True:

        edges = []
        values = []

        for v in prob.variables():
            if v.name.startswith('F') and v.varValue != 0:
                start = v.name.find('(')
                end = v.name.find(')')

                tup = tuple(v.name[start + 1:end].split(',_'))

                edges.append(tup)
                values.append(v.varValue)

        edges = [(int(i), int(j)) for i, j in edges]

        return total_abs_F, edges, values

    return total_abs_F
#TODO @SN I Would create a small class eg GraphDistance. it feels a bit weird that a flag (
# edge_flows) defines the number of return values, 1 vs 3. by creating a small container you can
# always return the same value and let the caller decide what they want to use. as a bonus you
# can load of a bit of logic and create a smaller function.

class GraphDistance:
    def __init__(self, prop):
        self._prop_variables = prop.variables

    @property
    def total_abs_F(self):
        total_abs_F = 0

        for v in self._prop_variables:
            if v.name.startswith('G'):
                total_abs_F += v.varValue
        return total_abs_F

    @property
    def eges(self):
        if not self._edges:
            self.calculate_edges_and_values()
        return self._edges

    @property
    def values(self):
        if not self._values:
            self.calculate_edges_and_values()
        return self._values

    def calculate_edges_and_values(self):
        edges = []
        values = []

        for v in self._prop_variables:
            if v.name.startswith('F') and v.varValue != 0:
                start = v.name.find('(')
                end = v.name.find(')')

                tup = tuple(v.name[start + 1:end].split(',_'))

                edges.append(tup)
                values.append(v.varValue)

        self._edges = [(int(i), int(j)) for i, j in edges]
        self._values = values
