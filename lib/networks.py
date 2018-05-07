import igraph as ig
import numpy as np

# Given a list of gene-gene interactions of some kind (pairs of genes treated as edges),
# construct a graph and, if specified, randomize it, preserving some invariant
def assemble_graph_of_interactions(edges, directed=False, randomize=False):
    interaction_graph = ig.Graph(directed=directed)
    vertex_names = np.unique(np.ravel(edges))
    interaction_graph.add_vertices(vertex_names)
    interaction_graph.add_edges(edges)

    if randomize:
        if directed:
            interaction_graph = interaction_graph.Degree_Sequence(
                interaction_graph.outdegree(),
                interaction_graph.indegree(),
                method='vl'
            )
        else:
            interaction_graph = interaction_graph.Degree_Sequence(
                interaction_graph.degree(),
                method='vl'
            )

    # Due to domain-related specifics,
    # directed graphs produced by this function
    # will represent marker-gene interactions
    # and must be bipartite therefore

    if directed:
        interaction_graph.vs["type"] = np.array(interaction_graph.outdegree()) == 0
    interaction_graph.vs["name"] = vertex_names
    return interaction_graph


''' TODO:   Стоит попробовать более совершенные метрики
            подобия, а также добиться лучшей скорости работы 
'''

# Given a pair of graphs, representing gene-gene interactions
# and estimated QTL-linkages, calculate for each pair of interacting genes
# a Jaccard similarity coefficient, and then average it over all edges
def mean_linkage_similarity(interaction_graph, QTL_graph):
    genes_with_linkages = QTL_graph.vs.select(type=1)["name"]
    genes_with_interactions = interaction_graph.vs["name"]

    subgraph_with_linkages = interaction_graph.subgraph(
        set(genes_with_linkages) & set(genes_with_interactions)
    )

    if not subgraph_with_linkages.ecount():
        return 0  # такой граф нет смысла проверять

    # Перебрать все рёбра и сопоставить каждому пару множеств —
    # eQTLs, которые линкуются с концами ребра —
    # а затем подсчитать для них долю общих элементов

    mean_jaccard = 0.
    for edge in subgraph_with_linkages.es:  # можно ли убрать этот цикл?
        source = subgraph_with_linkages.vs[edge.source]
        target = subgraph_with_linkages.vs[edge.target]

        s_neigh = set(QTL_graph.neighbors(source["name"], mode="IN"))
        t_neigh = set(QTL_graph.neighbors(target["name"], mode="IN"))
        mean_jaccard += len(s_neigh & t_neigh) / len(s_neigh | t_neigh)

    return mean_jaccard / subgraph_with_linkages.ecount()
