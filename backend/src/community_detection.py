import networkx as nx
from community import community_louvain
from collections import Counter


def detect_communities(G: nx.Graph):
    """
    Detecta comunidades usando Louvain directamente sobre NetworkX Graph
    """

    if G.number_of_nodes() == 0:
        return {
            "membership": {},
            "communities": []
        }

    # 🔹 Louvain
    partition = community_louvain.best_partition(
        G,
        weight="weight"
    )

    # 🔹 agrupar nodos por comunidad
    communities = {}
    for node, community_id in partition.items():
        communities.setdefault(community_id, []).append(node)

    result = []

    for community_id, members in communities.items():

        profiles = [
            G.nodes[m] for m in members
        ]

        companies = Counter()
        schools = Counter()
        locations = Counter()

        for profile in profiles:

            if not profile:
                continue

            location = profile.get("current_location")
            if location:
                locations[location] += 1

            for company in profile.get("companies", []):
                companies[company] += 1

            for university in profile.get("universities", []):
                schools[university] += 1

        result.append({
            "id": community_id,
            "size": len(members),
            "members": members,
            "top_companies": companies.most_common(5),
            "top_schools": schools.most_common(5),
            "top_locations": locations.most_common(5),
        })

    result.sort(key=lambda c: c["size"], reverse=True)

    return {
        "membership": partition,
        "communities": result
    }