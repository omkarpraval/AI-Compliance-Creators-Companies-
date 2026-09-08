import React from "react";
import { CheckCircle2, XCircle, AlertTriangle, Info } from "lucide-react";
import type { Verdict } from "@shared/index";

export interface VerdictBadgeProps {
  verdict: Verdict | "needs_review" | "approved" | "rejected" | "info";
  isDarkSurface?: boolean;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export const VerdictBadge: React.FC<VerdictBadgeProps> = ({
  verdict,
  isDarkSurface = false,
  className = "",
  size = "md",
}) => {
  // Normalize
  const v = verdict.toLowerCase();

  let text = "FLAGGED";
  let icon = <AlertTriangle className="w-3.5 h-3.5 shrink-0" />;
  let styleClass = "";

  if (v === "pass" || v === "approved") {
    text = v === "approved" ? "APPROVED" : "PASS";
    icon = <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />;
    styleClass = isDarkSurface
      ? "bg-[var(--pass-dark)] text-[var(--pass)] border border-[var(--pass)]/30"
      : "bg-[var(--pass-subtle)] text-[var(--pass)] border border-[var(--pass)]/20";
  } else if (v === "fail" || v === "rejected") {
    text = v === "rejected" ? "REJECTED" : "FAIL";
    icon = <XCircle className="w-3.5 h-3.5 shrink-0" />;
    styleClass = isDarkSurface
      ? "bg-[var(--fail-dark)] text-[var(--fail)] border border-[var(--fail)]/30"
      : "bg-[var(--fail-subtle)] text-[var(--fail)] border border-[var(--fail)]/20";
  } else if (v === "info") {
    text = "INFO";
    icon = <Info className="w-3.5 h-3.5 shrink-0" />;
    styleClass = isDarkSurface
      ? "bg-[var(--ev-raised)] text-[var(--info)] border border-[var(--info)]/30"
      : "bg-blue-50 text-[var(--info)] border border-blue-200";
  } else {
    // Flagged / needs_review
    text = v === "needs_review" ? "NEEDS REVIEW" : "FLAGGED";
    icon = <AlertTriangle className="w-3.5 h-3.5 shrink-0" />;
    styleClass = isDarkSurface
      ? "bg-[var(--flag-dark)] text-[var(--flag)] border border-[var(--flag)]/30"
      : "bg-[var(--flag-subtle)] text-[var(--flag)] border border-[var(--flag)]/20";
  }

  const heightClass = size === "sm" ? "h-[18px] text-[10px] px-2 gap-1" : size === "lg" ? "h-7 text-xs px-3 gap-1.5 font-semibold" : "h-[22px] text-xs px-2.5 gap-1.5 font-medium";

  return (
    <span
      className={`inline-flex items-center rounded-[var(--r-full)] tracking-wider uppercase font-mono-tabular select-none ${heightClass} ${styleClass} ${className}`}
    >
      {icon}
      <span>{text}</span>
    </span>
  );
};
