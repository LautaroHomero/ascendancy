from collections import defaultdict
from itertools import combinations

import networkx as nx

from normalize import normalize_degree
from location_utils import split_location


CATEGORIES = [
    "company",
    "university",
    "location",
    "position",
    "degree",
    "major"
]


def build_similarity_graph(profiles):
    """
    Construye un subgrafo independiente por cada tipo de atributo
    (company, university, location, position, degree, major). Una
    misma persona puede aparecer en varios de ellos.

    Retorna:
        {
            "company":    {"people": [...], "edges": [...]},
            "university": {"people": [...], "edges": [...]},
            ...
        }
    """

    if not profiles:
        return {
            category: {"people": [], "edges": []}
            for category in CATEGORIES
        }

    people = {}
    indexes = {category: defaultdict(set) for category in CATEGORIES}

    for person in profiles:

        person_id = f"person_{person['id']}"

        people[person_id] = {
            "id": person_id,
            "name": person["full_name"],
            "headline": person.get("headline"),
            "current_company": person.get("current_company_name"),
            "current_location": person.get("current_location"),
            "current_country": None,
            "current_city": None,
            "companies": [],
            "universities": [],
            "positions": [],
            "degrees": [],
            "majors": [],
        }

        if person.get("current_location"):

            country, city = split_location(person["current_location"])

            people[person_id]["current_country"] = country
            people[person_id]["current_city"] = city

            if country:
                indexes["location"][country].add(person_id)

        for exp in person.get("experience", []):

            company = exp.get("company")

            if company:

                company_name = company.get("name")

                if company_name:
                    indexes["company"][company_name].add(person_id)
                    people[person_id]["companies"].append(company_name)

            title = exp.get("title")

            if title:
                indexes["position"][title].add(person_id)
                people[person_id]["positions"].append(title)

        for edu in person.get("education", []):

            school = edu.get("school")

            if school:

                school_name = school.get("name")

                if school_name:
                    indexes["university"][school_name].add(person_id)
                    people[person_id]["universities"].append(school_name)

            for degree in edu.get("degrees", []):

                normalized = normalize_degree(degree)
                indexes["degree"][normalized].add(person_id)
                people[person_id]["degrees"].append(normalized)

            for major in edu.get("majors", []):

                indexes["major"][major].add(person_id)
                people[person_id]["majors"].append(major)

    graphs_by_category = {}

    for category in CATEGORIES:

        edges = {}
        people_in_category = set()

        def add_connection(person_a, person_b, value):

            key = tuple(sorted([person_a, person_b]))

            if key not in edges:
                edges[key] = {
                    "source": key[0],
                    "target": key[1],
                    "weight": 0,
                    "reasons": []
                }

            edges[key]["weight"] += 1
            edges[key]["reasons"].append({"type": category, "value": value})

        for value, persons in indexes[category].items():

            persons = list(persons)
            people_in_category.update(persons)

            if len(persons) < 2:
                continue

            for p1, p2 in combinations(persons, 2):
                add_connection(p1, p2, value)

        graphs_by_category[category] = {
            "people": [people[pid] for pid in people_in_category],
            "edges": list(edges.values())
        }

    return graphs_by_category


def build_mixed_graph(graphs_by_category):
    """
    Combina los 6 subgrafos por categoría en un único grafo mezclado:
    dos personas quedan conectadas si comparten CUALQUIER atributo.
    Reutiliza los edges ya calculados por categoría, fusionando los
    que conecten el mismo par de personas (suma weights, concatena
    reasons).
    """

    people = {}
    edges = {}

    for category_graph in graphs_by_category.values():

        for person in category_graph["people"]:
            people[person["id"]] = person

        for edge in category_graph["edges"]:

            key = tuple(sorted([edge["source"], edge["target"]]))

            if key not in edges:
                edges[key] = {
                    "source": key[0],
                    "target": key[1],
                    "weight": 0,
                    "reasons": []
                }

            edges[key]["weight"] += edge["weight"]
            edges[key]["reasons"].extend(edge["reasons"])

    return {
        "people": list(people.values()),
        "edges": list(edges.values())
    }


def _to_networkx(graph):

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
            weight=edge["weight"],
            reasons=edge["reasons"]
        )

    return G


def calculate_metrics(graph):

    G = _to_networkx(graph)

    if G.number_of_nodes() == 0:
        return {}

    degree = dict(G.degree())

    components = list(nx.connected_components(G))

    return {

        "nodes": G.number_of_nodes(),

        "edges": G.number_of_edges(),

        "density": round(
            nx.density(G),
            4
        ),

        "average_degree": round(
            sum(degree.values()) / len(degree),
            2
        ),

        "connected_components": len(components),

        "largest_component": max(
            len(c)
            for c in components
        ),

        "average_clustering": round(
            nx.average_clustering(
                G,
                weight="weight"
            ),
            4
        ),

        "degree": nx.degree_centrality(G),

        "betweenness": nx.betweenness_centrality(
            G,
            weight="weight"
        ),

        "closeness": nx.closeness_centrality(G),
    }


def graph_summary(graphs):

    summary = {}

    for category, graph in graphs.items():

        summary[category] = calculate_metrics(graph)

    return summary