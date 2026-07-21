import React from "react";

interface Props {
  status: string;
  source: string;
  minScore: number;
  sort: string;
  sources: string[];
  onStatusChange: (v: string) => void;
  onSourceChange: (v: string) => void;
  onMinScoreChange: (v: number) => void;
  onSortChange: (v: string) => void;
}

const STATUSES = ["", "new", "reviewed", "applied", "rejected", "interview"];

export default function FilterBar({
  status,
  source,
  minScore,
  sort,
  sources,
  onStatusChange,
  onSourceChange,
  onMinScoreChange,
  onSortChange,
}: Props) {
  return (
    <div className="filter-bar">
      <select value={status} onChange={(e) => onStatusChange(e.target.value)}>
        <option value="">All statuses</option>
        {STATUSES.filter(Boolean).map((s) => (
          <option key={s} value={s}>
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </option>
        ))}
      </select>

      <select value={source} onChange={(e) => onSourceChange(e.target.value)}>
        <option value="">All sources</option>
        {sources.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>

      <input
        type="number"
        min={0}
        max={100}
        value={minScore}
        onChange={(e) => onMinScoreChange(Number(e.target.value))}
        placeholder="Min score"
        style={{ width: 100 }}
      />

      <select value={sort} onChange={(e) => onSortChange(e.target.value)}>
        <option value="score">Sort by Score</option>
        <option value="scraped_at">Sort by Date</option>
        <option value="updated_at">Sort by Updated</option>
      </select>
    </div>
  );
}
