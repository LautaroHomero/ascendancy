"use client";

import { CATEGORY_KEYS, CATEGORY_LABELS, CategoryKey } from "../types/graph";

interface CategorySelectorProps {
  value: CategoryKey;
  onChange: (category: CategoryKey) => void;
}

export default function CategorySelector({
  value,
  onChange,
}: CategorySelectorProps) {
  return (
    <label className="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/80">
      <span className="font-mono text-[10px] uppercase tracking-[0.24em] text-white/45">
        group by
      </span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as CategoryKey)}
        className="min-w-40 bg-transparent font-mono text-sm text-white outline-none"
      >
        {CATEGORY_KEYS.map((key) => (
          <option key={key} value={key}>
            {CATEGORY_LABELS[key]}
          </option>
        ))}
      </select>
    </label>
  );
}
