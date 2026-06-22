def parse_profiles(data):

    nodes = {}
    edges = []

    def add_node(node_id, label, node_type):
        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "label": label,
                "type": node_type
            }

    def add_edge(source, target, relationship, **properties):
        edges.append({
            "source": source,
            "target": target,
            "relationship": relationship,
            **properties
        })

    for person in data["data"]:

        person_id = f"person_{person['id']}"

        add_node(
            person_id,
            person["full_name"],
            "person"
        )

        # CURRENT LOCATION
        current_location = person.get("current_location")

        if current_location:
            country_id = f"country_{current_location.lower().replace(' ', '_')}"

            add_node(
                country_id,
                current_location,
                "country"
            )

            add_edge(
                person_id,
                country_id,
                "LIVES_IN"
            )

        # EXPERIENCE
        for exp in person.get("experience", []):

            company = exp.get("company")

            if not company:
                continue

            company_name = company.get("name")

            if not company_name:
                continue

            company_id = (
                company.get("id")
                or company_name.lower().replace(" ", "_")
            )

            company_node = f"company_{company_id}"

            add_node(
                company_node,
                company_name,
                "company"
            )

            relation = (
                "CURRENTLY_WORKS_AT"
                if exp.get("is_current")
                else "WORKED_AT"
            )

            add_edge(
                person_id,
                company_node,
                relation,
                title=exp.get("title"),
                seniority=exp.get("seniority", []),
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date")
            )

            # INDUSTRY
            industry = company.get("industry")

            if industry:

                industry_id = (
                    "industry_" +
                    industry.lower().replace(" ", "_")
                )

                add_node(
                    industry_id,
                    industry,
                    "industry"
                )

                add_edge(
                    company_node,
                    industry_id,
                    "IN_INDUSTRY"
                )

            # COMPANY LOCATIONS
            for loc in company.get("locations", []):

                country = loc.get("country")
                state = loc.get("state")
                city = loc.get("city")

                country_node = None
                state_node = None
                city_node = None

                if country:

                    country_node = (
                        "country_" +
                        country.lower().replace(" ", "_")
                    )

                    add_node(
                        country_node,
                        country,
                        "country"
                    )

                if state:

                    state_node = (
                        "state_" +
                        state.lower().replace(" ", "_")
                    )

                    add_node(
                        state_node,
                        state,
                        "state"
                    )

                if city:

                    city_node = (
                        "city_" +
                        city.lower().replace(" ", "_")
                    )

                    add_node(
                        city_node,
                        city,
                        "city"
                    )

                if city_node and state_node:
                    add_edge(
                        city_node,
                        state_node,
                        "IN_STATE"
                    )

                if state_node and country_node:
                    add_edge(
                        state_node,
                        country_node,
                        "IN_COUNTRY"
                    )

                if city_node:
                    add_edge(
                        company_node,
                        city_node,
                        "LOCATED_IN"
                    )

        # EDUCATION
        for edu in person.get("education", []):

            school = edu.get("school")

            if not school:
                continue

            school_name = school.get("name")

            if not school_name:
                continue

            school_node = (
                "university_" +
                school_name.lower().replace(" ", "_")
            )

            add_node(
                school_node,
                school_name,
                "university"
            )

            add_edge(
                person_id,
                school_node,
                "STUDIED_AT"
            )

            for degree in edu.get("degrees", []):

                degree_node = (
                    "degree_" +
                    degree.lower().replace(" ", "_")
                )

                add_node(
                    degree_node,
                    degree,
                    "degree"
                )

                add_edge(
                    person_id,
                    degree_node,
                    "HAS_DEGREE"
                )

            for major in edu.get("majors", []):

                major_node = (
                    "major_" +
                    major.lower().replace(" ", "_")
                )

                add_node(
                    major_node,
                    major,
                    "major"
                )

                add_edge(
                    person_id,
                    major_node,
                    "STUDIED_MAJOR"
                )

    return nodes, edges