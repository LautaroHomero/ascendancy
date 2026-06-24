from collections import Counter

import networkx as nx


def build_networkx_graph(graph):
    """
    Converts one similarity graph into a NetworkX graph.

    Expected format:
    {
        "people": [...],
        "edges": [...]
    }
    """

    G = nx.Graph()

    for person in graph["people"]:
        G.add_node(
            person["id"],
            **person
        )

    for edge in graph["edges"]:
        G.add_edge(
            edge["source"],
            edge["target"],
            weight=edge.get("weight", 1),
            reasons=edge.get("reasons", [])
        )

    return G


def calculate_graph_metrics(graph):
    """
    Computes global graph metrics.
    """

    G = build_networkx_graph(graph)

    if G.number_of_nodes() == 0:
        return {
            "nodes": 0,
            "edges": 0,
            "density": 0,
            "average_degree": 0,
            "connected_components": 0,
            "largest_component": 0,
            "average_clustering": 0,
        }

    degrees = dict(G.degree())

    components = list(nx.connected_components(G))

    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": round(nx.density(G), 4),
        "average_degree": round(sum(degrees.values()) / len(degrees), 2),
        "connected_components": len(components),
        "largest_component": max(len(c) for c in components),
        "average_clustering": round(nx.average_clustering(G), 4),
    }


def calculate_centrality_metrics(graph):
    """
    Computes node centrality metrics.
    """

    G = build_networkx_graph(graph)

    if G.number_of_nodes() == 0:
        return {
            "degree": {},
            "betweenness": {},
            "closeness": {},
            "eigenvector": {},
        }

    degree = nx.degree_centrality(G)

    betweenness = nx.betweenness_centrality(
        G,
        weight="weight",
        normalized=True,
    )

    closeness = nx.closeness_centrality(G)

    try:
        eigenvector = nx.eigenvector_centrality(
            G,
            weight="weight",
            max_iter=1000,
        )
    except Exception:
        eigenvector = {}

    return {
        "degree": degree,
        "betweenness": betweenness,
        "closeness": closeness,
        "eigenvector": eigenvector,
    }


def top_nodes(graph, metric, limit=10):
    """
    Returns the highest-ranked nodes for a metric.
    """

    centrality = calculate_centrality_metrics(graph)

    values = centrality.get(metric, {})

    people = {
        p["id"]: p
        for p in graph["people"]
    }

    ranking = sorted(
        values.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    result = []

    for node_id, score in ranking[:limit]:

        person = people[node_id]

        result.append({
            "id": node_id,
            "name": person["name"],
            "headline": person.get("headline"),
            "score": round(score, 4)
        })

    return result


def graph_summary(graph):
    """
    Returns all metrics required by the frontend/report.
    """

    metrics = calculate_graph_metrics(graph)

    metrics["top_degree"] = top_nodes(
        graph,
        "degree"
    )

    metrics["top_betweenness"] = top_nodes(
        graph,
        "betweenness"
    )

    metrics["top_closeness"] = top_nodes(
        graph,
        "closeness"
    )

    metrics["top_eigenvector"] = top_nodes(
        graph,
        "eigenvector"
    )

    return metrics