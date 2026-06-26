from flask import Flask, jsonify
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@app.get("/people/<person_id>")
def get_person(person_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id,
                        name,
                        headline,
                        current_company,
                        current_location,
                        companies,
                        universities,
                        positions,
                        degrees,
                        majors
                    FROM people
                    WHERE id = %s
                    """,
                    (person_id,),
                )

                row = cur.fetchone()

        if row is None:
            return jsonify({"error": "Person not found"}), 404

        return jsonify(
            {
                "id": row[0],
                "name": row[1],
                "headline": row[2],
                "current_company": row[3],
                "current_location": row[4],
                "companies": row[5],
                "universities": row[6],
                "positions": row[7],
                "degrees": row[8],
                "majors": row[9],
            }
        )

    except Error:
        app.logger.exception("Database error")
        return jsonify({"error": "Database error"}), 500


if __name__ == "__main__":
    app.run(debug=True)