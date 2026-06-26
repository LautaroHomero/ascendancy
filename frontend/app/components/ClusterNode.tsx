"use client";

import { motion } from "framer-motion";
import { Handle, NodeProps, Position } from "reactflow";
import { CATEGORY_LABELS, TOP_FIELD_BY_CATEGORY } from "../types/graph";
import { ClusterNodeData } from "../utils/graphTransform";

function formatClusterLabel(raw: string, group?: number, maxLen = 52): string {

  const primary = raw.replace(/\s+\(\d+\)\s*$/i, "").trim();

  const label =
    group && group > 0
      ? `${primary} · group ${group}`
      : primary;

  return label.length > maxLen
    ? `${label.slice(0, maxLen - 1)}…`
    : label;
}
export default function ClusterNode({ data }: NodeProps<ClusterNodeData>) {
  const { cluster, category, maxSize, layout, isCentral } = data;
  const ratio = cluster.size / maxSize;
  const sizeBoost = Math.sqrt(ratio);
  const isGrid = layout === "grid";

  const density = cluster.size > 1
    ? cluster.edges.length / ((cluster.size * (cluster.size - 1)) / 2)
    : 0;

  const baseDiameter = isGrid ? 120 : isCentral ? 230 : 86 + sizeBoost * 170;

  const topField = TOP_FIELD_BY_CATEGORY[category];
  const topEntry = cluster[topField]?.[0];
  const topSignal = topEntry
    ? { label: CATEGORY_LABELS[category].toLowerCase(), value: topEntry[0] }
    : null;

  const fullLabel = cluster.label ?? topSignal?.value ?? `Cluster ${cluster.id}`;
  const displayName = formatClusterLabel(cluster.label ?? "", cluster.group)

  const hue = 199;
  const lightness = 55 + density * 20;
  const ringColor = `hsl(${hue}, 85%, ${lightness}%)`;

  return (
    <motion.div
      className="relative flex items-center justify-center"
      style={{ width: baseDiameter, height: baseDiameter }}
      whileHover={{ scale: 1.08 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />

      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: ringColor,
          opacity: 0.18 + density * 0.22,
          filter: `blur(${18 + density * 24}px)`,
        }}
      />

      {density > 0 && (
        <motion.div
          className="absolute inset-0 rounded-full border"
          style={{ borderColor: ringColor }}
          animate={{ opacity: [0.5, 0.15, 0.5], scale: [1, 1.12, 1] }}
          transition={{ duration: 2.4 + (1 - density) * 1.5, repeat: Infinity, ease: "easeInOut" }}
        />
      )}

      <div
      className="relative flex h-full w-full flex-col items-center justify-center rounded-full border cursor-pointer px-2"
      style={{
        background: `radial-gradient(circle at 35% 30%, hsla(${hue}, 70%, 35%, ${0.3 + density * 0.3}), rgba(10, 13, 20, 0.92))`,
        borderColor: ringColor,
        borderWidth: isCentral ? 1.5 : 1,
      }}
    >
      <span
          className="line-clamp-3 text-center text-[10px] font-medium leading-tight text-slate-200"
          title={fullLabel}
        >
          {displayName}
        </span>
        <span
          className="mt-1 font-mono font-semibold text-slate-50"
          style={{ fontSize: isGrid ? 20 : isCentral ? 36 : 16 + sizeBoost * 18 }}
        >
          {cluster.size}
        </span>
        <span className="font-mono text-[9px] text-slate-500">
          {cluster.size === 1 }
        </span>
      </div>

      {cluster.size === 1 && cluster.members[0] && (
        <span
          className="absolute -bottom-5 max-w-[140px] truncate text-center text-[9px] text-slate-500"
          title={cluster.members[0].name}
        >
          {cluster.members[0].name}
        </span>
      )}
    </motion.div>
  );
}
