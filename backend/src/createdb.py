import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Prefer a single DATABASE_URL env var, fall back to individual DB_* vars or hardcoded defaults
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    conn = psycopg2.connect(DATABASE_URL)
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "ascendancy")
    DB_USER = os.getenv("DB_USER", "lautarohomeroaguerreche")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
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
