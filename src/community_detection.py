import networkx as nx

from networkx.algorithms.community import louvain_communities


def _detect_communities_single(category_graph):
    """
    Corre la detección de comunidades sobre un único subgrafo
    (la lógica es la misma que la versión original de detect_communities,
    aplicada a un solo grafo en vez de al grafo global).
    """

    G = nx.Graph()

    for person in category_graph["people"]:

        G.add_node(

            person["id"],

            **person

        )

    for edge in category_graph["edges"]:

        G.add_edge(

            edge["source"],

            edge["target"],

            weight=edge["weight"],

            reasons=edge["reasons"]

        )

    clusters = []

    node_cluster = {}

    # Sin aristas: cada nodo es su propio cluster (caso "solo 1 persona").
    if G.number_of_edges() == 0:

        for cluster_id, node in enumerate(G.nodes()):

            node_cluster[node] = cluster_id

            clusters.append({

                "id": cluster_id,

                "size": 1,

                "members": [node]

            })

        return {

            "graph": G,

            "clusters": clusters,

            "node_cluster": node_cluster

        }

    communities = list(
        louvain_communities(
            G,
            weight="weight",
            seed=42,
        )
    )

    for cluster_id, community in enumerate(communities):

        members = list(community)

        for node in members:

            node_cluster[node] = cluster_id

        clusters.append({

            "id": cluster_id,

            "size": len(members),

            "members": members

        })

    # Louvain puede dejar nodos aislados fuera de las comunidades detectadas;
    # agregarlos como clusters de 1 para conservar perfiles sin conexiones.
    for node in G.nodes():

        if node in node_cluster:

            continue

        cluster_id = len(clusters)

        node_cluster[node] = cluster_id

        clusters.append({

            "id": cluster_id,

            "size": 1,

            "members": [node]

        })

    return {

        "graph": G,

        "clusters": clusters,

        "node_cluster": node_cluster

    }


def _detect_attribute_clusters(category_graph, attribute_key):
    """
    Un cluster por cada valor distinto del atributo (location, degree, etc.).
    """

    G = nx.Graph()

    for person in category_graph["people"]:

        G.add_node(person["id"], **person)

    for edge in category_graph["edges"]:

        G.add_edge(
            edge["source"],
            edge["target"],
            weight=edge["weight"],
            reasons=edge["reasons"],
        )

    by_value = {}

    for person in category_graph["people"]:

        if attribute_key == "degrees":

            for value in set(person.get("degrees") or []):

                by_value.setdefault(value, set()).add(person["id"])

        else:

            value = person.get(attribute_key)

            if not value:

                continue

            by_value.setdefault(value, set()).add(person["id"])

    clusters = []
    node_cluster = {}

    for cluster_id, (value, members) in enumerate(
        sorted(by_value.items(), key=lambda item: (-len(item[1]), item[0]))
    ):

        members = list(members)

        for member_id in members:

            node_cluster[member_id] = cluster_id

        clusters.append({

            "id": cluster_id,

            "size": len(members),

            "members": members,

            "value": value,

        })

    return {

        "graph": G,

        "clusters": clusters,

        "node_cluster": node_cluster,

    }


def _detect_location_clusters(category_graph):

    return _detect_attribute_clusters(category_graph, "current_country")


def _detect_degree_clusters(category_graph):

    return _detect_attribute_clusters(category_graph, "degrees")


def detect_communities(graphs_by_category):
    """
    Recibe el dict de subgrafos por categoria (salida de
    build_similarity_graph) y corre la detección de comunidades
    en cada uno por separado.

    Retorna:
        {
            "company":    {"graph": G, "clusters": [...], "node_cluster": {...}},
            "university": {...},
            ...
        }
    """

    return {
        category: (
            _detect_location_clusters(category_graph)
            if category == "location"
            else _detect_degree_clusters(category_graph)
            if category == "degree"
            else _detect_communities_single(category_graph)
        )
        for category, category_graph in graphs_by_category.items()
    }
