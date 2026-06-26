"use client";

import { useEffect, useState } from "react";
import { Person } from "../types/graph";

interface InsightItem {
  company_name?: string;
  university_name?: string;
  major_name?: string;      // Mapeado desde la columna 'majors'
  position_name?: string;   // Mapeado desde la columna 'positions'
  count: string;
}

interface InsightsData {
  companies: InsightItem[];
  universities: InsightItem[];
  majors: InsightItem[];       // 🚀 Sincronizado con tu JSONB 'majors'
  positions: InsightItem[];    // 🚀 Sincronizado con tu JSONB 'positions'
  location: {
    same_city: number;
    same_country: number;
  };
}

interface PersonPanelProps {
  person: Person;
  onClose: () => void;
}

export default function PersonPanel({ person, onClose }: PersonPanelProps) {
  const [insights, setInsights] = useState<InsightsData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchInsights() {
      setLoading(true);
      try {
        const res = await fetch(`/api/person-insights?id=${person.id}`);
        const data = await res.json();
        setInsights(data);
      } catch (err) {
        console.error("Error fetching insights:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchInsights();
  }, [person.id]);

  return (
    <div className="absolute right-4 top-16 z-30 w-96 max-h-[80vh] overflow-y-auto rounded-xl border border-white/10 bg-black/90 p-4 text-white backdrop-blur">
      {/* Header */}
      <div className="mb-4 flex justify-between items-start">
        <div>
          <h2 className="text-lg font-semibold">{person.name}</h2>
          {person.headline && <p className="text-sm text-white/60">{person.headline}</p>}
        </div>
        <button onClick={onClose} className="text-white/50 hover:text-white p-1">✕</button>
      </div>

      {/* Basic Info */}
      <div className="space-y-3 mb-4">
        {person.current_company && (
          <div>
            <div className="text-xs uppercase text-white/40">Current Company</div>
            <div className="text-sm">{person.current_company}</div>
          </div>
        )}
        {person.current_location && (
          <div>
            <div className="text-xs uppercase text-white/40">Location</div>
            <div className="text-sm">{person.current_location}</div>
          </div>
        )}
      </div>

      {/* Network Insights Section */}
      <div className="border-t border-white/10 pt-4">
        <h3 className="text-xs uppercase text-green-400 font-semibold mb-2">Network Insights</h3>
        
        {loading ? (
          <div className="text-sm text-white/40 animate-pulse">Loading shared connections...</div>
        ) : insights ? (
          <div className="space-y-4 text-sm">
            
            {/* Shared Companies */}
            <div>
              <div className="text-xs text-white/50">Company colleagues in your network:</div>
              {insights.companies.length > 0 ? (
                <ul className="mt-1 space-y-1">
                  {insights.companies.map((c, i) => (
                    <li key={i} className="text-xs bg-white/5 p-1.5 rounded flex justify-between">
                      <span className="truncate max-w-[200px]">{c.company_name}</span>
                      <span className="text-green-400 font-medium">+{c.count} people</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-xs text-white/30 italic">No one else shares their past companies.</div>
              )}
            </div>

            {/* Shared Universities */}
            <div>
              <div className="text-xs text-white/50">Alumni in your network:</div>
              {insights.universities.length > 0 ? (
                <ul className="mt-1 space-y-1">
                  {insights.universities.map((u, i) => (
                    <li key={i} className="text-xs bg-white/5 p-1.5 rounded flex justify-between">
                      <span className="truncate max-w-[200px]">{u.university_name}</span>
                      <span className="text-green-400 font-medium">+{u.count} people</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-xs text-white/30 italic">No one else shares their universities.</div>
              )}
            </div>

            {/* 🚀 NEW: Shared Majors (Lo que estudiaron lo mismo) */}
            <div>
              <div className="text-xs text-white/50">People who studied the same majors:</div>
              {insights.majors && insights.majors.length > 0 ? (
                <ul className="mt-1 space-y-1">
                  {insights.majors.map((m, i) => (
                    <li key={i} className="text-xs bg-white/5 p-1.5 rounded flex justify-between">
                      <span className="truncate max-w-[200px]">{m.major_name}</span>
                      <span className="text-green-400 font-medium">+{m.count} people</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-xs text-white/30 italic">No one else shares their academic major.</div>
              )}
            </div>

            {/* 🚀 NEW: Shared Positions (Misma posición/cargo) */}
            <div>
              <div className="text-xs text-white/50">People who held the same positions:</div>
              {insights.positions && insights.positions.length > 0 ? (
                <ul className="mt-1 space-y-1">
                  {insights.positions.map((p, i) => (
                    <li key={i} className="text-xs bg-white/5 p-1.5 rounded flex justify-between">
                      <span className="truncate max-w-[200px]">{p.position_name}</span>
                      <span className="text-green-400 font-medium">+{p.count} people</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-xs text-white/30 italic">No one else shares their past positions.</div>
              )}
            </div>

            {/* Geographic Distribution */}
            {insights.location && (
              <div className="border-t border-white/10 pt-3 mt-3 space-y-1">
                <div className="text-xs text-white/50">Geographic Distribution:</div>

                {insights.location.same_city > 0 && person.current_city && (
                  <div className="text-xs bg-white/5 p-1.5 rounded flex justify-between">
                    <span>Live in {person.current_city}</span>
                    <span className="text-green-400 font-medium">+{insights.location.same_city} people</span>
                  </div>
                )}

                {insights.location.same_country > 0 && person.current_country && (
                  <div className="text-xs bg-white/5 p-1.5 rounded flex justify-between">
                    <span>Live in {person.current_country}</span>
                    <span className="text-green-400 font-medium">+{insights.location.same_country} people</span>
                  </div>
                )}
              </div>
            )}

          </div>
        ) : (
          <div className="text-xs text-red-400">Failed to load insights.</div>
        )}
      </div>
    </div>
  );
}