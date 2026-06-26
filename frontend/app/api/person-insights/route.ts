import { NextResponse } from "next/server";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL, 
});

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const personId = searchParams.get("id");

  if (!personId) {
    return NextResponse.json({ error: "Missing person ID" }, { status: 400 });
  }

  try {
    const client = await pool.connect();

    // 1. Find company colleagues in common
    const companiesQuery = `
      SELECT c.company_name, COUNT(p.id) as count
      FROM people p,
           jsonb_array_elements_text((SELECT companies FROM people WHERE id = $1)) AS c(company_name)
      WHERE p.companies @> jsonb_build_array(c.company_name) AND p.id != $1
      GROUP BY c.company_name;
    `;

    // 2. Find alumni from the same universities
    const universitiesQuery = `
      SELECT u.university_name, COUNT(p.id) as count
      FROM people p,
           jsonb_array_elements_text((SELECT universities FROM people WHERE id = $1)) AS u(university_name)
      WHERE p.universities @> jsonb_build_array(u.university_name) AND p.id != $1
      GROUP BY u.university_name;
    `;

    // 3. Find people who studied the same majors
    const majorsQuery = `
      SELECT m.major_name, COUNT(p.id) as count
      FROM people p,
           jsonb_array_elements_text((SELECT majors FROM people WHERE id = $1)) AS m(major_name)
      WHERE p.majors @> jsonb_build_array(m.major_name) AND p.id != $1
      GROUP BY m.major_name;
    `;

    // 4. Find people who held the same positions/roles
    const positionsQuery = `
      SELECT pos.position_name, COUNT(p.id) as count
      FROM people p,
           jsonb_array_elements_text((SELECT positions FROM people WHERE id = $1)) AS pos(position_name)
      WHERE p.positions @> jsonb_build_array(pos.position_name) AND p.id != $1
      GROUP BY pos.position_name;
    `;

    // 5. Find how many people live in the same City and Country
    const locationQuery = `
      SELECT 
        (SELECT COUNT(*) FROM people WHERE current_city = target.current_city AND id != target.id) as same_city_count,
        (SELECT COUNT(*) FROM people WHERE current_country = target.current_country AND id != target.id) as same_country_count
      FROM people target
      WHERE target.id = $1;
    `;

    const companiesResult = await client.query(companiesQuery, [personId]);
    const universitiesResult = await client.query(universitiesQuery, [personId]);
    const majorsResult = await client.query(majorsQuery, [personId]);
    const positionsResult = await client.query(positionsQuery, [personId]);
    const locationResult = await client.query(locationQuery, [personId]);
    
    client.release();

    const locationData = locationResult.rows[0] || { same_city_count: 0, same_country_count: 0 };

    return NextResponse.json({
      companies: companiesResult.rows,
      universities: universitiesResult.rows,
      majors: majorsResult.rows,
      positions: positionsResult.rows,
      location: {
        same_city: parseInt(locationData.same_city_count),
        same_country: parseInt(locationData.same_country_count)
      }
    });

  } catch (error) {
    console.error("Error in person-insights API:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}