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

        # 🟢 SOLUCIÓN: Validar que 'experience' sea una lista antes de iterar
        experiences = person.get("experience")
        if isinstance(experiences, list):
            for exp in experiences:
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

        # 🟢 SOLUCIÓN: Validar que 'education' sea una lista antes de iterar
        educations = person.get("education")
        if isinstance(educations, list):
            for edu in educations:
                if not isinstance(edu, dict):
                    continue

                school = edu.get("school")
                if isinstance(school, dict):
                    school_name = school.get("name")
                    if school_name:
                        indexes["university"][school_name].add(person_id)
                        people[person_id]["universities"].append(school_name)

                # 🟢 SOLUCIÓN: Validar que 'degrees' sea una lista
                degrees = edu.get("degrees")
                if isinstance(degrees, list):
                    for degree in degrees:
                        if not degree:
                            continue
                        normalized = normalize_degree(degree)
                        indexes["degree"][normalized].add(person_id)
                        people[person_id]["degrees"].append(normalized)

                # 🟢 SOLUCIÓN: Validar que 'majors' sea una lista
                majors = edu.get("majors")
                if isinstance(majors, list):
                    for major in majors:
                        if not major:
                            continue
                        indexes["major"][major].add(person_id)
                        people[person_id]["majors"].append(major)

    # (El resto de la función para armar las conexiones queda exactamente igual...)
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
            "edges": list(edges.values()),
        }

    return graphs_by_category