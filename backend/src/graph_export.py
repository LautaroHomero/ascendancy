def export_graph_for_frontend(G, partition=None):
    """
    Convierte un NetworkX graph en formato compatible con frontend (Next.js + D3/ForceGraph/etc)
    """

    nodes = []
    links = []

    # 🔹 nodos
    for node_id, attrs in G.nodes(data=True):

        node = {
            "id": node_id,
            "name": attrs.get("name"),
            "headline": attrs.get("headline"),
            "current_company": attrs.get("current_company"),
            "current_location": attrs.get("current_location"),
        }

        # si tenés comunidades (Louvain)
        if partition and node_id in partition:
            node["group"] = partition[node_id]

        nodes.append(node)

    # 🔹 links
    for source, target, attrs in G.edges(data=True):
        links.append({
            "source": source,
            "target": target,
            "weight": attrs.get("weight", 1),
            "reasons": attrs.get("reasons", [])
        })

    return {
        "nodes": nodes,
        "links": links
    }