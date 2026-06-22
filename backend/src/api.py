# api.py

from flask import Flask, jsonify
import psycopg2
import json

app = Flask(__name__)

conn = psycopg2.connect(
    dbname="ascendancy",
    user="lautarohomeroaguerreche"
)

@app.get("/people/<person_id>")
def get_person(person_id):

    cur = conn.cursor()

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
        (person_id,)
    )

    row = cur.fetchone()

    if not row:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "id": row[0],
        "name": row[1],
        "headline": row[2],
        "current_company": row[3],
        "current_location": row[4],
        "companies": row[5],
        "universities": row[6],
        "positions": row[7],
        "degrees": row[8],
        "majors": row[9]
    })

if __name__ == "__main__":
    app.run(debug=True)