import React, { useState } from "react";
import { ArrowUpDown, ChevronDown, ChevronUp } from "lucide-react";

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
  align?: "left" | "center" | "right";
  width?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  isLoading?: boolean;
  emptyMessage?: string;
  isDarkSurface?: boolean;
}

export function DataTable<T extends { id?: string | number }>({
  columns,
  data,
  onRowClick,
  isLoading = false,
  emptyMessage = "No records found.",
  isDarkSurface = false,
}: DataTableProps<T>) {
  const [density, setDensity] = useState<"comfortable" | "compact">("comfortable");
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortAsc, setSortAsc] = useState(true);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  const sortedData = [...data].sort((a: any, b: any) => {
    if (!sortKey) return 0;
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    if (aVal === bVal) return 0;
    if (aVal == null) return 1;
    if (bVal == null) return -1;
    const res = aVal > bVal ? 1 : -1;
    return sortAsc ? res : -res;
  });

  const rowHeightClass = density === "comfortable" ? "h-[52px]" : "h-[38px]";

  const tableBg = isDarkSurface ? "bg-[var(--ev-surface)]" : "bg-[var(--doc-surface)]";
  const borderColor = isDarkSurface ? "border-[var(--ev-line)]" : "border-[var(--doc-line)]";
  const headerBg = isDarkSurface ? "bg-[var(--ev-raised)]" : "bg-[var(--doc-bg)]";
  const textColor = isDarkSurface ? "text-[var(--ev-text)]" : "text-[var(--doc-text)]";
  const textMuted = isDarkSurface ? "text-[var(--ev-text-muted)]" : "text-[var(--doc-text-muted)]";

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (data.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, data.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Enter" && selectedIndex >= 0 && onRowClick) {
      e.preventDefault();
      onRowClick(sortedData[selectedIndex]);
    }
  };

  return (
    <div className="w-full flex flex-col gap-2" onKeyDown={handleKeyDown} tabIndex={0}>
      {/* Density toggle controls */}
      <div className="flex justify-end items-center gap-2 mb-1">
        <span className={`text-xs ${textMuted}`}>Density:</span>
        <button
          onClick={() => setDensity("comfortable")}
          className={`px-2 py-0.5 text-xs rounded-[var(--r-xs)] border ${
            density === "comfortable"
              ? "bg-[var(--brand)] text-white border-[var(--brand)]"
              : `bg-transparent ${textColor} ${borderColor}`
          }`}
        >
          Comfortable
        </button>
        <button
          onClick={() => setDensity("compact")}
          className={`px-2 py-0.5 text-xs rounded-[var(--r-xs)] border ${
            density === "compact"
              ? "bg-[var(--brand)] text-white border-[var(--brand)]"
              : `bg-transparent ${textColor} ${borderColor}`
          }`}
        >
          Compact
        </button>
      </div>

      {/* Table container */}
      <div className={`overflow-x-auto rounded-[var(--r-md)] border ${borderColor} ${tableBg} shadow-xs`}>
        <table className="w-full border-collapse text-left text-xs">
          <thead className={`sticky top-0 z-10 ${headerBg} border-b ${borderColor}`}>
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => col.sortable && handleSort(col.key)}
                  className={`px-4 py-3 font-semibold ${textColor} ${
                    col.sortable ? "cursor-pointer select-none hover:text-[var(--brand)]" : ""
                  } ${col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left"}`}
                  style={{ width: col.width }}
                >
                  <div className="inline-flex items-center gap-1.5">
                    <span>{col.header}</span>
                    {col.sortable && (
                      <span className="text-[var(--doc-text-faint)]">
                        {sortKey === col.key ? (
                          sortAsc ? <ChevronUp className="w-3.5 h-3.5 text-[var(--brand)]" /> : <ChevronDown className="w-3.5 h-3.5 text-[var(--brand)]" />
                        ) : (
                          <ArrowUpDown className="w-3 h-3 opacity-40 hover:opacity-100" />
                        )}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className={`divide-y ${borderColor}`}>
            {sortedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className={`px-4 py-8 text-center ${textMuted}`}>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sortedData.map((item, idx) => {
                const isSelected = selectedIndex === idx;
                return (
                  <tr
                    key={(item as any).id || idx}
                    onClick={() => onRowClick && onRowClick(item)}
                    className={`${rowHeightClass} transition-colors duration-[var(--dur-instant)] ${
                      onRowClick ? "cursor-pointer" : ""
                    } ${
                      isSelected
                        ? isDarkSurface
                          ? "bg-[var(--brand-subtle-d)] border-l-2 border-l-[var(--brand)]"
                          : "bg-[var(--brand-subtle)]/40 border-l-2 border-l-[var(--brand)]"
                        : isDarkSurface
                        ? "hover:bg-[var(--ev-raised)]"
                        : "hover:bg-[var(--brand-subtle)]/20"
                    }`}
                  >
                    {columns.map((col) => (
                      <td
                        key={col.key}
                        className={`px-4 ${textColor} ${
                          col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left"
                        }`}
                      >
                        {col.render ? col.render(item) : (item as any)[col.key] ?? "—"}
                      </td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
