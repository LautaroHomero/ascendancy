"use client";

import { useMemo, useState } from "react";
import { CategoryKey, GraphDataByCategory } from "../types/graph";
import CategorySelector from "./CategorySelector";
import GraphView from "./GraphView";

interface GraphPageClientProps {
  graphsByCategory: GraphDataByCategory;
}

export default function GraphPageClient({ graphsByCategory }: GraphPageClientProps) {
  const [category, setCategory] = useState<CategoryKey>("company");
  
  const activeGraph = useMemo(
    () => graphsByCategory[category],
    [graphsByCategory, category]
  );

  const isEmpty = useMemo(() => {
    if (!activeGraph) return true;
    
    const hasPeople = activeGraph.people && activeGraph.people.length > 0;
    const hasClusters = activeGraph.clusters && activeGraph.clusters.length > 0;
    
    return !hasPeople && !hasClusters;
  }, [activeGraph]);

  return (
    <div className="relative min-h-screen overflow-hidden bg-black">
      <div className="absolute left-1/2 top-4 z-20 flex -translate-x-1/2 items-center gap-3">
        <CategorySelector value={category} onChange={setCategory} />
        <div className="inline-flex rounded-full border border-white/10 bg-white/5 p-1 text-xs text-white/70 backdrop-blur">
          <button
            type="button"
            className={`rounded-full px-3 py-1 transition ${
             "bg-white text-black" 
            }`}
          >
            Community
          </button>
        </div>
      </div>

      {isEmpty ? (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-white/50">
          <p className="text-lg font-medium">No data available</p>
          <p className="text-sm text-white/30">Run the backend with a JSON.</p>
        </div>
      ) : (
        <GraphView graph={activeGraph} category={category} />
      )}
    </div>
  );
}