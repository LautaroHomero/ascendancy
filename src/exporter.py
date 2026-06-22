from collections import Counter
from collections import defaultdict
import json

from location_utils import split_location


# Mapea cada categoria al campo top_* que corresponde, para poder
# elegir el nombre del cluster sin un if/elif repetido por categoria.
_TOP_FIELD_BY_CATEGORY = {
    "company": "top_companies",
    "university": "top_universities",
    "location": "top_locations",
    "position": "top_positions",
    "degree": "top_degrees",
    "major": "top_majors",
}


def _count_member_attributes(members):
    """Cuenta atributos directamente de los miembros (incluye clusters de 1)."""

    companies = Counter()
    universities = Counter()
    locations = Counter()
    positions = Counter()
    degrees = Counter()
    majors = Counter()

    for person in members:

        for value in set(person.get("companies") or []):

            companies[value] += 1

        for value in set(person.get("universities") or []):

            universities[value] += 1

        if person.get("current_location"):

            locations[person["current_location"]] += 1

        for value in set(person.get("positions") or []):

            positions[value] += 1

        for value in set(person.get("degrees") or []):

            degrees[value] += 1

        for value in set(person.get("majors") or []):

            majors[value] += 1

    return {
        "top_companies": companies.most_common(10),
        "top_universities": universities.most_common(10),
        "top_locations": locations.most_common(10),
        "top_positions": positions.most_common(10),
        "top_degrees": degrees.most_common(10),
        "top_majors": majors.most_common(10),
    }


def _build_cluster_export(cluster_id, members, label):
    member_tops = _count_member_attributes(members)

    return {
        "id": cluster_id,
        "size": len(members),
        "label": label,
        "name": label,
        "members": members,
        "edges": [],
        "top_companies": member_tops["top_companies"],
        "top_universities": member_tops["top_universities"],
        "top_locations": member_tops["top_locations"],
        "top_positions": member_tops["top_positions"],
        "top_degrees": member_tops["top_degrees"],
        "top_majors": member_tops["top_majors"],
    }


def _cluster_name(cluster_export, category, size, location_value=None):
    """
    Nombre del cluster: el valor mas frecuente de la categoria que
    le dio origen (ej. en "university", el nombre de la universidad
    mas comun dentro del cluster), seguido de la cantidad de personas.

    Si el cluster no tiene ningun edge interno (clusters de 1 sola
    persona, sin conexiones), no hay un top valor para usar, y se cae
    a un nombre generico con el id del cluster.
    """

    if category in ("location", "degree") and location_value:

        return f"{location_value} ({size} personas)"

    top_field = _TOP_FIELD_BY_CATEGORY[category]

    top_values = cluster_export[top_field]

    if not top_values:

        return f"Cluster {cluster_export['id']} ({size} personas)"

    top_value, _count = top_values[0]

    return f"{top_value} ({size} personas)"


def _disambiguate_cluster_names(exported_clusters, category):
    """
    Si varios clusters comparten el mismo nombre base (ej. tres
    componentes distintos con Clemson University), agrega un sufijo.
    """

    seen = Counter()

    for cluster_export in exported_clusters:

        name = cluster_export.get("label") or cluster_export["name"]
        base = name.rsplit(" (", 1)[0]

        seen[base] += 1

        if seen[base] > 1:

            duplicate_name = (
                f"{base} · grupo {cluster_export['id']} ({cluster_export['size']} personas)"
            )

            cluster_export["name"] = duplicate_name
            cluster_export["label"] = duplicate_name


def _export_location_category(category_graph):
    people = category_graph["people"]

    grouped = defaultdict(lambda: defaultdict(list))
    uncategorized = []

    for person in people:

        country = person.get("current_country")
        city = person.get("current_city")

        if not country:
            country, city = split_location(person.get("current_location"))

        if not country:
            uncategorized.append(person)
            continue

        city_label = city or country
        grouped[country][city_label].append(person)

    exported_clusters = []

    for country_id, country in enumerate(
        sorted(grouped.keys(), key=lambda value: (-sum(len(members) for members in grouped[value].values()), value))
    ):

        cities = grouped[country]
        country_members = [
            person
            for city_members in cities.values()
            for person in city_members
        ]

        city_exports = []

        for city_id, (city, city_members) in enumerate(
            sorted(cities.items(), key=lambda item: (-len(item[1]), item[0]))
        ):

            city_exports.append(
                _build_cluster_export(
                    f"{country_id}-{city_id}",
                    city_members,
                    city,
                )
            )

        country_export = _build_cluster_export(
            country_id,
            country_members,
            country,
        )
        country_export["cities"] = city_exports

        exported_clusters.append(country_export)

    if uncategorized:
        exported_clusters.append(
            _build_cluster_export(
                len(exported_clusters),
                uncategorized,
                "Sin ubicación",
            )
        )

    return {
        "stats": {
            "people": len(people),
            "connections": 0,
            "clusters": len(exported_clusters),
            "countries": len(grouped) + (1 if uncategorized else 0),
            "cities": sum(len(cities) for cities in grouped.values()),
        },
        "people": people,
        "edges": [],
        "clusters": exported_clusters,
    }


def _export_category(category_graph, category_community_data, category):
    """
    Exporta una única categoría (ej: "company") con la misma lógica
    de la versión original de export_graph: arma los clusters con
    sus top_companies/top_universities/etc., pero ahora a partir de
    un subgrafo de una sola categoría.
    """

    if category == "location":
        return _export_location_category(category_graph)

    G = category_community_data["graph"]

    clusters = category_community_data["clusters"]

    people_lookup = {

        person["id"]: person

        for person in category_graph["people"]

    }

    edge_lookup = {}

    for edge in category_graph["edges"]:

        key = tuple(

            sorted(

                [

                    edge["source"],

                    edge["target"]

                ]

            )

        )

        edge_lookup[key] = edge

    exported_clusters = []

    for cluster in clusters:

        members = []

        companies = Counter()
        universities = Counter()
        locations = Counter()
        positions = Counter()
        degrees = Counter()
        majors = Counter()

        internal_edges = []

        for member_id in cluster["members"]:

            person = people_lookup[member_id]

            members.append(person)

        member_tops = _count_member_attributes(members)

        for i in range(len(cluster["members"])):

            for j in range(i + 1, len(cluster["members"])):

                p1 = cluster["members"][i]

                p2 = cluster["members"][j]

                key = tuple(sorted([p1, p2]))

                edge = edge_lookup.get(key)

                if not edge:

                    continue

                internal_edges.append(edge)

                for reason in edge["reasons"]:

                    t = reason["type"]

                    value = reason["value"]

                    if t == "company":

                        companies[value] += 1

                    elif t == "university":

                        universities[value] += 1

                    elif t == "location":

                        locations[value] += 1

                    elif t == "position":

                        positions[value] += 1

                    elif t == "degree":

                        degrees[value] += 1

                    elif t == "major":

                        majors[value] += 1

        # Preferir conteos de edges cuando existen; si no (cluster de 1),
        # usar los atributos de los miembros directamente.
        def pick_top(edge_counter, member_key):

            from_edges = edge_counter.most_common(10)

            if from_edges:

                return from_edges

            return member_tops[member_key]

        cluster_export = {
            "id": cluster["id"],
            "size": cluster["size"],
            "members": members,
            "edges": internal_edges,
            "top_companies": pick_top(companies, "top_companies"),
            "top_universities": pick_top(universities, "top_universities"),
            "top_locations": pick_top(locations, "top_locations"),
            "top_positions": pick_top(positions, "top_positions"),
            "top_degrees": pick_top(degrees, "top_degrees"),
            "top_majors": pick_top(majors, "top_majors"),
        }

        cluster_export["label"] = _cluster_name(
            cluster_export,
            category,
            cluster["size"],
            location_value=cluster.get("value"),
        )
        cluster_export["name"] = cluster_export["label"]

        exported_clusters.append(cluster_export)

    _disambiguate_cluster_names(exported_clusters, category)

    return {

        "stats": {

            "people": G.number_of_nodes(),

            "connections": G.number_of_edges(),

            "clusters": len(exported_clusters)

        },

        "people": category_graph["people"],

        "edges": category_graph["edges"],

        "clusters": exported_clusters

    }


def export_graph(
    graphs_by_category,
    community_data_by_category,
    output_path
):
    """
    Exporta los 6 subgrafos (uno por categoria), cada uno con sus
    propios clusters y stats, a un único archivo graph.json.

    Forma del output:
        {
            "company":    { "stats", "people", "edges", "clusters" },
            "university": { ... },
            "location":   { ... },
            "position":   { ... },
            "degree":     { ... },
            "major":      { ... }
        }
    """

    output = {

        category: _export_category(
            graphs_by_category[category],
            community_data_by_category[category],
            category
        )

        for category in graphs_by_category

    }

    with open(

        output_path,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            output,

            f,

            indent=4,

            ensure_ascii=False

        )

    print()

    print("=====================================")
    print("Graph exported successfully")
    print("=====================================")
    print()

    for category, data in output.items():

        stats = data["stats"]

        print(
            f"[{category}] "
            f"people={stats['people']} "
            f"connections={stats['connections']} "
            f"clusters={stats['clusters']}"
        )
