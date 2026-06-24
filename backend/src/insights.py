from typing import Dict, List


def generate_insights(metrics: Dict, communities: Dict) -> List[str]:
    """
    Generate human-readable insights from graph metrics.
    """

    insights = []

    nodes = metrics["nodes"]
    edges = metrics["edges"]
    density = metrics["density"]
    avg_degree = metrics["average_degree"]
    clustering = metrics["average_clustering"]
    components = metrics["connected_components"]

    community_list = communities["communities"]

    #
    # Density
    #
    if density < 0.01:
        insights.append(
            "The network is sparse, indicating that most professionals share relatively few direct similarities."
        )
    elif density < 0.05:
        insights.append(
            "The network has a moderate density, with several overlapping professional relationships."
        )
    else:
        insights.append(
            "The network is highly interconnected."
        )

    #
    # Connected Components
    #
    if components == 1:
        insights.append(
            "All profiles belong to a single connected component."
        )
    else:
        insights.append(
            f"The graph contains {components} connected components, suggesting the existence of disconnected professional groups."
        )

    #
    # Average degree
    #
    if avg_degree < 2:
        insights.append(
            "Profiles tend to have relatively few similarity connections."
        )
    elif avg_degree < 5:
        insights.append(
            "Profiles have a moderate number of similarity connections."
        )
    else:
        insights.append(
            "Profiles are highly interconnected."
        )

    #
    # Clustering coefficient
    #
    if clustering > 0.5:
        insights.append(
            "Strong local clusters exist, indicating tightly related professional groups."
        )
    elif clustering > 0.2:
        insights.append(
            "Several local communities are present in the network."
        )
    else:
        insights.append(
            "Local clustering is relatively weak."
        )

    #
    # Communities
    #
    if community_list:

        largest = community_list[0]

        percentage = round(
            largest["size"] / nodes * 100,
            1
        )

        insights.append(
            f"The largest community contains {largest['size']} profiles ({percentage}% of the network)."
        )

        if largest["top_companies"]:

            company = largest["top_companies"][0][0]

            insights.append(
                f"The largest community is primarily centered around professionals associated with {company}."
            )

        if largest["top_schools"]:

            school = largest["top_schools"][0][0]

            insights.append(
                f"Educational background also plays an important role, with {school} appearing frequently within the largest community."
            )

    #
    # Size
    #
    if nodes > 500:
        insights.append(
            "The dataset is large enough to reveal meaningful community structures."
        )

    #
    # Connectivity
    #
    ratio = edges / nodes if nodes else 0

    if ratio < 1:
        insights.append(
            "Most professionals are connected to only a small number of similar profiles."
        )

    return insights


def assumptions():
    """
    Assumptions made while constructing the graph.
    """

    return [
        "Each LinkedIn profile is represented as a node.",
        "Edges represent similarity relationships rather than real social connections.",
        "Professional experience, education, industry and skills contribute to similarity.",
        "Company and school names are normalized before comparison whenever possible.",
        "Profiles with missing information may have fewer connections."
    ]


def limitations():
    """
    Current project limitations.
    """

    return [
        "Similarity is heuristic and does not imply actual professional relationships.",
        "Incomplete LinkedIn profiles reduce graph connectivity.",
        "Different spellings of organizations may still generate duplicate entities.",
        "Edge weights are based on manually selected similarity rules.",
        "The analysis ignores temporal information such as employment dates."
    ]


def next_steps():
    """
    Possible future improvements.
    """

    return [
        "Use semantic embeddings instead of exact text matching.",
        "Include temporal career analysis.",
        "Predict potential professional relationships using link prediction.",
        "Store the graph in Neo4j for advanced querying.",
        "Analyze how communities evolve over time."
    ]