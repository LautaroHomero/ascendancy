import psycopg2
import json
conn = psycopg2.connect(
    host="localhost",
    database="ascendancy",
    user="lautarohomeroaguerreche",
    password="postgres"
)

def save_people(people):

    cur = conn.cursor()

    for person in people:

        cur.execute(
            """
            INSERT INTO people (
                id,
                name,
                headline,

                current_company,
                current_location,
                current_country,
                current_city,

                companies,
                universities,
                positions,
                degrees,
                majors
            )
            VALUES (
                %s,%s,%s,
                %s,%s,%s,%s,
                %s,%s,%s,%s,%s
            )
            ON CONFLICT (id)
            DO UPDATE SET
                name = EXCLUDED.name,
                headline = EXCLUDED.headline,
                current_company = EXCLUDED.current_company,
                current_location = EXCLUDED.current_location,
                current_country = EXCLUDED.current_country,
                current_city = EXCLUDED.current_city,
                companies = EXCLUDED.companies,
                universities = EXCLUDED.universities,
                positions = EXCLUDED.positions,
                degrees = EXCLUDED.degrees,
                majors = EXCLUDED.majors
            """,
            (
                person["id"],
                person.get("name"),
                person.get("headline"),

                person.get("current_company"),
                person.get("current_location"),
                person.get("current_country"),
                person.get("current_city"),

                json.dumps(person.get("companies", [])),
                json.dumps(person.get("universities", [])),
                json.dumps(person.get("positions", [])),
                json.dumps(person.get("degrees", [])),
                json.dumps(person.get("majors", [])),
            ),
        )

    conn.commit()

    print(f"Saved {len(people)} people")
def create_database():
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id TEXT PRIMARY KEY,
            name TEXT,
            headline TEXT,
            current_company TEXT,
            current_location TEXT,
            current_country TEXT,
            current_city TEXT,
            companies JSONB,
            universities JSONB,
            positions JSONB,
            degrees JSONB,
            majors JSONB
        )
    """)
    
    cur.execute("TRUNCATE TABLE people;") 
    
    conn.commit()
