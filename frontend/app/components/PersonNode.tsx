"use client";

import { Handle, NodeProps, Position } from "reactflow";
import { PersonNodeData } from "../utils/graphTransform";

export default function PersonNode({ data }: NodeProps<PersonNodeData>) {
  const { person, internalDegree, isCore} = data;
  const backgroundColor = isCore ? "#16a34a" : "#1e40af";
  return (
    <div className="flex w-[200px] items-center gap-2 rounded-lg border border-slate-700/60 bg-slate-900/90 px-3 py-2 transition-colors hover:border-sky-500/60">
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />

      <div
        className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full font-mono text-[10px] text-slate-200"
        style={{
          backgroundColor:backgroundColor
        }}
      >
        {internalDegree}
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate text-xs font-medium text-slate-100">{person.name}</p>
        <p className="truncate font-mono text-[10px] text-slate-500">
          {person.current_company ?? person.headline ?? "—"}
        </p>
        {person.current_location && (
          <p className="truncate font-mono text-[10px] text-slate-600">
            {person.current_location}
          </p>
        )}
      </div>
    </div>
  );
}