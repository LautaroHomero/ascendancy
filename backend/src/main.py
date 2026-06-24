import json
import os

import networkx as nx

from graph_export import export_graph_for_frontend
from similarity_graph import (
    build_similarity_graph,
    build_mixed_graph,
    _to_networkx
)
from load_data import load_profiles
from community_detection import detect_communities


def main():

    print("Loading profiles...")

    profiles = load_profiles("../data/X Connections.json")

    print(f"Loaded {len(profiles)} profiles")

    print("Building similarity graph...")

    graphs_by_category = build_similarity_graph(profiles)
    mixed_graph = build_mixed_graph(graphs_by_category)

    G = _to_networkx(mixed_graph)

    print(f"{G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    print("Detecting communities...")

    result = detect_communities(G)

    frontend_graph = export_graph_for_frontend(
        G,
        partition=result["membership"]
    )

    output = {
        "graph": frontend_graph,
        "communities": result["communities"]
    }

    # 🔥 NUEVO: escribir a frontend
    write_to_json_file(output)

    print("✅ Graph exported to frontend successfully")

    return output

def write_to_json_file(data, output_path="graph.json"):
    """
    Escribe data como JSON en una ruta local.
    No tiene dependencia del frontend.
    """

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"📁 JSON written to: {output_path}")

if __name__ == "__main__":
    main()