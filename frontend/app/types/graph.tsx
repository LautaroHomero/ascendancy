export interface Person {
  id: string;
  name: string;
  headline: string | null;

  current_company: string | null;
  current_location: string | null;

  current_country?: string | null;
  current_city?: string | null;

  companies: string[];
  universities: string[];
  positions: string[];
  degrees: string[];
  majors: string[];
}
  export interface EdgeReason {
    type: "company" | "university" | "location" | "position" | "degree" | "major";
    value: string;
  }
  
  export interface GraphEdge {
    source: string;
    target: string;
    weight: number;
    reasons: EdgeReason[];
  }
  
  export type CountTuple = [string, number];
  
  export interface Cluster {
    id: number;
    size: number;
    /** Human-readable label from the backend export (`name` in graph.json). */
    label?: string;
    core_type?: string;
    core_value?: string;
    members: Person[];
    edges: GraphEdge[];
    cities?: Cluster[];
    top_companies: CountTuple[];
    top_universities: CountTuple[];
    top_locations: CountTuple[];
    top_positions: CountTuple[];
    top_degrees: CountTuple[];
    top_majors: CountTuple[];
    group?:number;
  }
  
  export interface GraphStats {
    people: number;
    connections: number;
    clusters: number;
  }
  
  export interface GraphData {
    stats: GraphStats;
    people: Person[];
    edges: GraphEdge[];
    clusters: Cluster[];
  }
  
  export const CATEGORY_KEYS = [
    "company",
    "university",
    "location",
    "position",
    "degree",
    "major",
  ] as const;
  
  export type CategoryKey = (typeof CATEGORY_KEYS)[number];
  
  export const CATEGORY_LABELS: Record<CategoryKey, string> = {
    company: "Company",
    university: "University",
    location: "Location",
    position: "Position",
    degree: "Degree",
    major: "Major",
  };

  export const TOP_FIELD_BY_CATEGORY: Record<
    CategoryKey,
    keyof Pick<
      Cluster,
      | "top_companies"
      | "top_universities"
      | "top_locations"
      | "top_positions"
      | "top_degrees"
      | "top_majors"
    >
  > = {
    company: "top_companies",
    university: "top_universities",
    location: "top_locations",
    position: "top_positions",
    degree: "top_degrees",
    major: "top_majors",
  };
  
  export type GraphDataByCategory = Record<CategoryKey, GraphData>;
