import dagre from "@dagrejs/dagre";
import { Node, Edge, Position } from "reactflow";
import { CategoryKey, Cluster, GraphData, Person } from "../types/graph";

const CLUSTER_NODE_WIDTH = 180;
const CLUSTER_NODE_HEIGHT = 180;
const PERSON_NODE_WIDTH = 200;
const PERSON_NODE_HEIGHT = 64;

const PERSON_FIELD_BY_CATEGORY: Record<CategoryKey, keyof Person | null> = {
  company: "companies",
  university: "universities",
  position: "positions",
  degree: "degrees",
  major: "majors",
  location: null, // location se maneja distinto, ver abajo
};

function seededNoise(seed: string) {
  let hash = 0;

  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) >>> 0;
  }

  return (offset = 0) => {
    const value = Math.sin(hash + offset * 97.13) * 10000;
    return value - Math.floor(value);
  };
}

export interface ClusterNodeData {
  kind: "cluster";
  cluster: Cluster;
  category: CategoryKey;
  maxSize: number;
  layout: "grid" | "radial";
  isCentral: boolean;
}

export interface PersonNodeData {
  kind: "person";
  person: Person;
  internalDegree: number;
  isCore: boolean;
}

export type AscendancyNodeData = ClusterNodeData | PersonNodeData;

function layout<T extends AscendancyNodeData>(
  nodes: Node<T>[],
  edges: Edge[],
  nodeWidth: number,
  nodeHeight: number,
  direction: "TB" | "LR" = "TB"
) {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: direction, nodesep: 60, ranksep: 90 });

  nodes.forEach((node) => {
    g.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });

  dagre.layout(g);

  return nodes.map((node) => {
    const { x, y } = g.node(node.id);
    return {
      ...node,
      position: { x: x - nodeWidth / 2, y: y - nodeHeight / 2 },
      targetPosition: direction === "TB" ? Position.Top : Position.Left,
      sourcePosition: direction === "TB" ? Position.Bottom : Position.Right,
    };
  });
}

function circleLayout<T extends AscendancyNodeData>(
  nodes: Node<T>[],
  innerRadius = 120,
  outerRadiusStep = 110
) {
  if (nodes.length === 0) {
    return nodes;
  }

  const center = nodes[0];
  const outer = nodes.slice(1);

  if (outer.length === 0) {
    return [
      {
        ...center,
        position: { x: 0, y: 0 },
      },
    ];
  }

  const shells: Node<T>[][] = [];
  const perShell = Math.max(6, Math.ceil(Math.sqrt(outer.length) * 2));

  for (let index = 0; index < outer.length; index += perShell) {
    shells.push(outer.slice(index, index + perShell));
  }

  const positioned: Node<T>[] = [
    {
      ...center,
      position: { x: 0, y: 0 },
    },
  ];

  shells.forEach((shell, shellIndex) => {
    const radius = innerRadius + shellIndex * outerRadiusStep;
    const angleOffset = (shellIndex % 2) * (Math.PI / shell.length);

    shell.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / shell.length - Math.PI / 2 + angleOffset;
      positioned.push({
        ...node,
        position: {
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
        },
      });
    });
  });

  return positioned;
}

/**
 * Overview view: a planet-like radial distribution, with the largest group
 * at the center and the rest floating around it at varying distances.
 */
export function buildClusterOverview(
  graph: GraphData,
  category: CategoryKey
): {
  nodes: Node<ClusterNodeData>[];
  edges: Edge[];
} {
  const maxSize = Math.max(...graph.clusters.map((c) => c.size), 1);
  const sorted = [...graph.clusters].sort((a, b) => b.size - a.size);

  const nodes: Node<ClusterNodeData>[] = sorted.map((cluster, i) => {
    const noise = seededNoise(String(cluster.id));
    const position = (() => {
      if (i === 0) return { x: 0, y: 0 };

      const normalized = cluster.size / maxSize;
      const orbitStrength = Math.pow(1 - normalized, 1.25);
      const shell = Math.floor((i - 1) / 8);
      const ringRadius = 120 + orbitStrength * 420 + shell * 75;
      const angle = noise(2) * Math.PI * 2 - Math.PI;
      const radialJitter = (noise(1) - 0.5) * (80 + orbitStrength * 90);
      const lateralJitter = (noise(3) - 0.5) * 120;
      const verticalJitter = (noise(4) - 0.5) * 120;

      return {
        x: Math.cos(angle) * (ringRadius + radialJitter) + lateralJitter,
        y: Math.sin(angle) * (ringRadius + radialJitter) + verticalJitter,
      };
    })();

    return {
      id: `cluster-${cluster.id}`,
      type: "clusterNode",
      position,
      data: {
        kind: "cluster",
        cluster,
        category,
        maxSize,
        layout: "radial",
        isCentral: i === 0,
      },
      width: CLUSTER_NODE_WIDTH,
      height: CLUSTER_NODE_HEIGHT,
    };
  });

  return { nodes, edges: [] };
}

export function buildClusterExpansion(
  cluster: Cluster,
  category: CategoryKey,
  maxEdges = 150
): { nodes: Node<PersonNodeData>[]; edges: Edge[] } {

  const memberIds = new Set(cluster.members.map((m) => m.id));

  const degree = new Map<string, number>();

  cluster.edges.forEach((e) => {

    if (!memberIds.has(e.source) || !memberIds.has(e.target)) {
      return;
    }

    degree.set(
      e.source,
      (degree.get(e.source) ?? 0) + 1
    );

    degree.set(
      e.target,
      (degree.get(e.target) ?? 0) + 1
    );
  });

  const sortedEdges = [...cluster.edges]
    .filter(
      (e) =>
        memberIds.has(e.source) &&
        memberIds.has(e.target)
    )
    .sort((a, b) => b.weight - a.weight)
    .slice(0, maxEdges);

  const topDegree = Math.max(
    ...Array.from(degree.values()),
    1
  );

  const rawNodes: Node<PersonNodeData>[] =
  cluster.members.map((person) => {
    const internalDegree = degree.get(person.id) ?? 0;

    return {
      id: person.id,
      type: "personNode",
      position: { x: 0, y: 0 },
      data: {
        kind: "person",
        person,
        internalDegree,
        isCore: isCoreMember(person, cluster, category) , // 👈 leer del backend, no recalcular
      },
      width: PERSON_NODE_WIDTH,
      height: PERSON_NODE_HEIGHT,
    };
  });

  const rawEdges: Edge[] = sortedEdges.map(
    (e, i) => ({
      id: `e-${i}-${e.source}-${e.target}`,

      source: e.source,

      target: e.target,

      style: {
        strokeWidth: Math.min(
          1 + e.weight / 4,
          6
        ),
        opacity: 0.45,
      },
    })
  );

  const nodes = layout(
    rawNodes,
    rawEdges,
    PERSON_NODE_WIDTH,
    PERSON_NODE_HEIGHT,
    "LR"
  );

  return {
    nodes,
    edges: rawEdges,
  };
}
function isCoreMember(
  person: Person,
  cluster: Cluster,
  category: CategoryKey
): boolean {
  if (category === "location") {
    return !!person.current_location &&
           (person.current_location.includes(cluster.label?? "") ?? false);
  }

  const field = PERSON_FIELD_BY_CATEGORY[category];
  if (!field) return false;

  const clusterValue = cluster.label?.split(" (")[0];
  if (!clusterValue) return false;

  const personValues = person[field] as string[] | undefined;
  return personValues?.includes(clusterValue) ?? false;
}

export function buildLocationCityExpansion(
  cluster: Cluster,
  category:CategoryKey,
  maxEdges = 150
): { nodes: Node<PersonNodeData>[]; edges: Edge[] } {
  if (cluster.members.length === 0) {
    return { nodes: [], edges: [] };
  }

  const hub = cluster.members[0];
  const rawNodes: Node<PersonNodeData>[] = cluster.members.map((person) => ({
    id: person.id,
    type: "personNode",
    position: { x: 0, y: 0 },
    data: {
      kind: "person",
      person,
      internalDegree: person.id === hub.id ? Math.max(cluster.members.length - 1, 0) : 1,
      isCore: isCoreMember(person, cluster, category),
    },
    width: PERSON_NODE_WIDTH,
    height: PERSON_NODE_HEIGHT,
  }));

  const rawEdges: Edge[] = cluster.members
    .slice(1, maxEdges)
    .map((person, index) => ({
      id: `loc-${cluster.id}-${index}-${hub.id}-${person.id}`,
      source: hub.id,
      target: person.id,
      style: {
        strokeWidth: 1,
        opacity: 0.35,
      },
    }));

  const nodes = layout(rawNodes, rawEdges, PERSON_NODE_WIDTH, PERSON_NODE_HEIGHT, "LR");

  return { nodes, edges: rawEdges };
}


