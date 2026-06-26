"use client";

import { useCallback, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Node,
  NodeMouseHandler,
  ReactFlowProvider,
} from "reactflow";
import "reactflow/dist/style.css";
import PersonPanel from "./PersonalPanel";
import { CategoryKey, GraphData, Person } from "../types/graph";
import {
  AscendancyNodeData,
  buildClusterExpansion,
  buildClusterOverview,
  buildLocationCityExpansion,
} from "../utils/graphTransform";
import ClusterNode from "./ClusterNode";
import PersonNode from "./PersonNode";

const nodeTypes = {
  clusterNode: ClusterNode,
  personNode: PersonNode,
};



interface GraphViewProps {
  graph: GraphData;
  category: CategoryKey;
}



export default function GraphView({ graph, category }: GraphViewProps) {
  const isLocation = category === "location";
  const [expandedClusterId, setExpandedClusterId] = useState<number | null>(null);
  const [selectedCountryId, setSelectedCountryId] = useState<number | null>(null);
  const [selectedCityId, setSelectedCityId] = useState<number | null>(null);

const [selectedPerson, setSelectedPerson] = useState<Person | null>(null);

  const overview = useMemo(() => buildClusterOverview(graph, category), [graph, category]);

  const expandedCluster = useMemo(
    () => graph.clusters.find((cluster) => cluster.id === expandedClusterId) ?? null,
    [graph, expandedClusterId]
  );

  const selectedCountry = useMemo(
    () => (isLocation ? graph.clusters.find((cluster) => cluster.id === selectedCountryId) ?? null : null),
    [graph, isLocation, selectedCountryId]
  );

  const selectedCity = useMemo(
    () => selectedCountry?.cities?.find((city) => city.id === selectedCityId) ?? null,
    [selectedCountry, selectedCityId]
  );

  const cityOverview = useMemo(() => {
    if (!selectedCountry) {
      return null;
    }

    const cityGraph = {
      ...graph,
      clusters: selectedCountry.cities ?? [],
    } as GraphData;

    return buildClusterOverview(cityGraph, category);
  }, [category, graph, selectedCountry]);
  

  const clusterExpansion = useMemo(
    () => {
      if (!expandedCluster) {
        return null;
      }

      return buildClusterExpansion(expandedCluster,category);
    },
    [expandedCluster]
  );

  const locationExpansion = useMemo(
    () => {
      if (!selectedCity) {
        return null;
      }

      return  buildLocationCityExpansion(selectedCity, category);
    },
    [selectedCity]
  );

  const nodes = isLocation
    ? locationExpansion?.nodes ?? cityOverview?.nodes ?? overview.nodes
    : clusterExpansion?.nodes ?? overview.nodes;

  const edges = isLocation
    ? locationExpansion?.edges ?? cityOverview?.edges ?? overview.edges
    : clusterExpansion?.edges ?? overview.edges;
  
  const highlightedEdges = useMemo(() => {

      if (!selectedPerson) {
        return edges;
      }
    
      return edges.map((edge) => {
    
        const isConnected =
          edge.source === selectedPerson.id ||
          edge.target === selectedPerson.id;
    
        return {
          ...edge,
          animated: isConnected,
    
          style: {
            ...edge.style,
            strokeWidth: isConnected ? 5 : 1,
            opacity: isConnected ? 1 : 0.08,
            stroke: isConnected ? "#22c55e" : "#6b7280",
          },
        };
      });
    
    }, [edges, selectedPerson]);

    const highlightedNodes = useMemo(() => {

      if (!selectedPerson) {
        return nodes;
      }
    
      const connectedIds = new Set<string>();
    
      edges.forEach((edge) => {
    
        if (edge.source === selectedPerson.id) {
          connectedIds.add(edge.target);
        }
    
        if (edge.target === selectedPerson.id) {
          connectedIds.add(edge.source);
        }
      });
    
      connectedIds.add(selectedPerson.id);
    
      return nodes.map((node) => {
    
        const isConnected = connectedIds.has(node.id);
    
        return {
          ...node,
          style: {
            ...(node.style ?? {}),
            opacity: isConnected ? 1 : 0.15,
          },
        };
      });
    
    }, [nodes, edges, selectedPerson]);

  const handleNodeClick: NodeMouseHandler = useCallback(
  (_, node: Node<AscendancyNodeData>) => {

    if (node.data.kind === "person") {

      setSelectedPerson(node.data.person);

      return;
    }

    if (isLocation) {

      if (!selectedCountry) {
        setSelectedCountryId(node.data.cluster.id);
        return;
      }

      if (!selectedCity) {
        setSelectedCityId(node.data.cluster.id);
      }

      return;
    }

    setExpandedClusterId(node.data.cluster.id);
  },
  [isLocation, selectedCity, selectedCountry]
);

  const handleBack = useCallback(() => {
    setSelectedPerson(null);
    if (isLocation) {
      if (selectedCity) {
        setSelectedCityId(null);
        return;
      }

      if (selectedCountry) {
        setSelectedCountryId(null);
        return;
      }
    }

    setExpandedClusterId(null);
  }, [isLocation, selectedCity, selectedCountry]);

  const showBack = isLocation
    ? Boolean(selectedCountry || selectedCity)
    : Boolean(expandedCluster);

    return (
      <div className="absolute inset-0">
        {showBack && (
          <button
            onClick={handleBack}
            className="absolute left-4 top-16 z-20 rounded-full border border-white/10 bg-black/70 px-3 py-1 text-xs text-white/70 backdrop-blur"
          >
            ← back
          </button>
        )}
  
        <ReactFlowProvider>
          <ReactFlow
            nodes={highlightedNodes}
            edges={highlightedEdges}
            nodeTypes={nodeTypes}
            onNodeClick={handleNodeClick}
            fitView
            fitViewOptions={{ padding: 0.2, duration: 400, minZoom: 0.15, maxZoom: 1.25 }}
            proOptions={{ hideAttribution: true }}
            nodesDraggable={Boolean(clusterExpansion || locationExpansion)}
            nodesConnectable={false}
          >
            <Background color="#111827" gap={28} />
          </ReactFlow>
  
          {/* Renderizado condicional del nuevo componente */}
          {selectedPerson && (
            <PersonPanel 
              person={selectedPerson} 
              onClose={() => setSelectedPerson(null)} 
            />
          )}
        </ReactFlowProvider>
      </div>
    );
}


