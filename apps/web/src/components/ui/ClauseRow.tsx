import React from "react";
import type { Clause, ClauseVerdict, Verdict } from "@shared/index";
import { VerdictBadge } from "./VerdictBadge";
import { ConfidenceMeter } from "./ConfidenceMeter";

export interface ClauseRowProps {
  clauseRef: string;
  requirement: string;
  verdict?: Verdict | "needs_review" | "pass" | "fail" | "flagged";
  confidence?: number;
  isSelected?: boolean;
  isOverridden?: boolean;
  overrideVerdict?: Verdict | null;
  severity?: "critical" | "standard" | "advisory";
  onClick?: () => void;
  onHover?: () => void;
  className?: string;
  isDarkSurface?: boolean;
}

export const ClauseRow: React.FC<ClauseRowProps> = ({
  clauseRef,
  requirement,
  verdict,
  confidence = 1.0,
  isSelected = false,
  isOverridden = false,
  overrideVerdict,
  severity = "standard",
  onClick,
  onHover,
  className = "",
  isDarkSurface = true,
}) => {
  const activeVerdict = isOverridden && overrideVerdict ? overrideVerdict : verdict;

  const bgStyle = isDarkSurface
    ? isSelected
      ? "bg-[var(--ev-raised)] border-l-2 border-l-[var(--brand)] text-[var(--ev-text)]"
      : "bg-[var(--ev-surface)] hover:bg-[var(--ev-raised)] text-[var(--ev-text)] border-l-2 border-l-transparent"
    : isSelected
    ? "bg-white border-l-2 border-l-[var(--brand)] text-[var(--doc-text)] shadow-xs"
    : "bg-white hover:bg-[var(--doc-bg)] text-[var(--doc-text)] border-l-2 border-l-transparent";

  const borderColor = isDarkSurface ? "border-[var(--ev-line)]" : "border-[var(--doc-line)]";

  return (
    <div
      onClick={onClick}
      onMouseEnter={onHover}
      className={`group relative p-3 rounded-[var(--r-sm)] border ${borderColor} ${bgStyle} cursor-pointer transition-all duration-[var(--dur-fast)] select-none ${className}`}
    >
      <div className="flex items-start justify-between gap-2.5">
        <div className="flex items-center gap-2">
          <span className="font-mono-tabular text-xs font-semibold text-[var(--brand)] bg-[var(--brand-subtle-d)] px-1.5 py-0.5 rounded-[var(--r-xs)] border border-[var(--brand)]/30">
            {clauseRef}
          </span>
          {severity === "critical" && (
            <span className="text-[10px] uppercase font-bold tracking-wider text-[var(--fail)] bg-[var(--fail-dark)] px-1.5 py-0.2 rounded-[var(--r-xs)]">
              Critical
            </span>
          )}
        </div>

        {activeVerdict && (
          <div className="flex items-center gap-1.5">
            {isOverridden && (
              <span className="text-[9px] uppercase tracking-wider text-[var(--ev-text-faint)] line-through">
                {verdict}
              </span>
            )}
            <VerdictBadge verdict={activeVerdict} isDarkSurface={isDarkSurface} size="sm" />
          </div>
        )}
      </div>

      <p
        className={`mt-1.5 text-xs leading-relaxed line-clamp-2 ${
          isDarkSurface ? "text-[var(--ev-text)]" : "text-[var(--doc-text)]"
        }`}
      >
        {requirement}
      </p>

      <div className="mt-2.5 flex items-center justify-between pt-1 border-t border-[var(--ev-line)]/50">
        <ConfidenceMeter confidence={confidence} showText />
        {isOverridden && (
          <span className="text-[10px] font-mono-tabular text-[var(--brand)] font-medium">
            Overridden
          </span>
        )}
      </div>
    </div>
  );
};
