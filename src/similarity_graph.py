from collections import defaultdict
from itertools import combinations

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
    Construye un subgrafo independiente por cada tipo de atributo.

    A diferencia de la versión anterior (que mezclaba las 6 categorías
    en un solo grafo), esta función devuelve 6 grafos separados, uno
    por categoria. Una misma persona puede aparecer en varios de ellos.

    Retorna:
        {
            "company":    {"people": [...], "edges": [...]},
            "university": {"people": [...], "edges": [...]},
            "location":   {"people": [...], "edges": [...]},
            "position":   {"people": [...], "edges": [...]},
            "degree":     {"people": [...], "edges": [...]},
            "major":      {"people": [...], "edges": [...]},
        }
    """

    people = {}

    # indexes[categoria][valor] = set de person_ids con ese valor
    indexes = {category: defaultdict(set) for category in CATEGORIES}

    # --------------------------------------------------
    # PERSONAS + INDEXAR POR CATEGORIA
    # --------------------------------------------------

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

        # ---------------------------------------------
        # CURRENT LOCATION
        # ---------------------------------------------

        if person.get("current_location"):

            country, city = split_location(person["current_location"])

            people[person_id]["current_country"] = country
            people[person_id]["current_city"] = city

            if country:

                indexes["location"][country].add(person_id)

        # ---------------------------------------------
        # EXPERIENCE
        # ---------------------------------------------

        for exp in person.get("experience", []):

            company = exp.get("company")

            if company:

                company_name = company.get("name")

                if company_name:

                    indexes["company"][
                        company_name
                    ].add(person_id)

                    people[person_id]["companies"].append(company_name)

            title = exp.get("title")

            if title:

                indexes["position"][
                    title
                ].add(person_id)

                people[person_id]["positions"].append(title)

        # ---------------------------------------------
        # EDUCATION
        # ---------------------------------------------

        for edu in person.get("education", []):

            school = edu.get("school")

            if school:

                school_name = school.get("name")

                if school_name:

                    indexes["university"][
                        school_name
                    ].add(person_id)

                    people[person_id]["universities"].append(school_name)

            for degree in edu.get("degrees", []):

                normalized = normalize_degree(degree)

                indexes["degree"][
                    normalized
                ].add(person_id)

                people[person_id]["degrees"].append(normalized)

            for major in edu.get("majors", []):

                indexes["major"][
                    major
                ].add(person_id)

                people[person_id]["majors"].append(major)

    # ======================================================
    # ARMAR UN SUBGRAFO POR CATEGORIA
    # ======================================================

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

            edges[key]["reasons"].append({
                "type": category,
                "value": value
            })

        for value, persons in indexes[category].items():

            persons = list(persons)

            # Incluir a todos, aunque estén solos en ese valor
            # (ej. una ciudad con una sola persona).
            people_in_category.update(persons)

            if len(persons) < 2:
                continue

            for p1, p2 in combinations(persons, 2):

                add_connection(p1, p2, value)

        graphs_by_category[category] = {
            "people": [
                people[pid] for pid in people_in_category
            ],
            "edges": list(edges.values())
        }

    return graphs_by_category
