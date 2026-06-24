from graph_metrics import graph_summary
from community_detection import detect_communities
from insights import (
    generate_insights,
    assumptions,
    limitations,
    next_steps,
)


def build_report(graph):
    """
    Generates the complete graph analysis report.
    """

    metrics = graph_summary(graph)

    communities = detect_communities(graph)

    observations = generate_insights(
        metrics,
        communities
    )

    report = {
        "summary": {
            "nodes": metrics["nodes"],
            "edges": metrics["edges"],
            "density": metrics["density"],
            "average_degree": metrics["average_degree"],
            "connected_components": metrics["connected_components"],
            "largest_component": metrics["largest_component"],
            "average_clustering": metrics["average_clustering"],
            "communities": len(communities["communities"])
        },

        "rankings": {
            "degree": metrics["top_degree"],
            "betweenness": metrics["top_betweenness"],
            "closeness": metrics["top_closeness"],
            "eigenvector": metrics["top_eigenvector"]
        },

        "communities": communities["communities"],

        "insights": observations,

        "assumptions": assumptions(),

        "limitations": limitations(),

        "next_steps": next_steps()
    }

    return report