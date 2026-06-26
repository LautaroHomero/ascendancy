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
    "major",
]


def build_similarity_graph(profiles):

    if not profiles:
        return {
            category: {
                "people": [],
                "edges": [],
            }
            for category in CATEGORIES
        }

    people = {}
    indexes = {category: defaultdict(set) for category in CATEGORIES}

    for person in profiles:

        # Skip malformed profiles
        if not isinstance(person, dict):
            continue

        person_id = person.get("id")
        full_name = person.get("full_name")

        # Skip profiles missing required fields
        if not person_id or not full_name:
            continue

        person_id = f"person_{person_id}"

        people[person_id] = {
            "id": person_id,
            "name": full_name,
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

        current_location = person.get("current_location")

        if current_location:

            country, city = split_location(current_location)

            people[person_id]["current_country"] = country
            people[person_id]["current_city"] = city

            if country:
                indexes["location"][country].add(person_id)

        for exp in person.get("experience") or []:

            if not isinstance(exp, dict):
                continue

            company = exp.get("company")

            if isinstance(company, dict):

                company_name = company.get("name")

                if company_name:

                    indexes["company"][company_name].add(person_id)
                    people[person_id]["companies"].append(company_name)

            title = exp.get("title")

            if title:

                indexes["position"][title].add(person_id)
                people[person_id]["positions"].append(title)

        for edu in person.get("education") or []:

            if not isinstance(edu, dict):
                continue

            school = edu.get("school")

            if isinstance(school, dict):

                school_name = school.get("name")

                if school_name:

                    indexes["university"][school_name].add(person_id)
                    people[person_id]["universities"].append(school_name)

            for degree in edu.get("degrees") or []:

                if not degree:
                    continue

                normalized = normalize_degree(degree)

                indexes["degree"][normalized].add(person_id)
                people[person_id]["degrees"].append(normalized)

            for major in edu.get("majors") or []:

                if not major:
                    continue

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
                    "reasons": [],
                }

            edges[key]["weight"] += 1

            edges[key]["reasons"].append(
                {
                    "type": category,
                    "value": value,
                }
            )

        for value, persons in indexes[category].items():

            persons = list(persons)

            people_in_category.update(persons)

            if len(persons) < 2:
                continue

            for p1, p2 in combinations(persons, 2):
                add_connection(p1, p2, value)

        graphs_by_category[category] = {
            "people": [people[pid] for pid in people_in_category],
            "edges": list(edges.values()),
        }

    return graphs_by_category