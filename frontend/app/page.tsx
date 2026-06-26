import GraphPageClient from "./components/GraphPageClient";
import graphData from "../public/graph.json";
import { GraphDataByCategory } from "./types/graph";

export default function Home() {
  const graphsByCategory = graphData as unknown as GraphDataByCategory;

  return (
    <main className="min-h-screen bg-black">
      <GraphPageClient graphsByCategory={graphsByCategory} />
    </main>
  );
}
