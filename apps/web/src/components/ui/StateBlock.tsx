import React from "react";
import { AlertCircle, FileSearch, Inbox, Loader2 } from "lucide-react";
import { Button } from "./Button";

export interface StateBlockProps {
  type: "empty" | "loading" | "error";
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
  isDarkSurface?: boolean;
}

export const StateBlock: React.FC<StateBlockProps> = ({
  type,
  title,
  description,
  actionLabel,
  onAction,
  className = "",
  isDarkSurface = false,
}) => {
  let icon = <Inbox className="w-10 h-10 text-[var(--doc-text-faint)]" />;
  if (type === "loading") {
    icon = <Loader2 className="w-10 h-10 animate-spin text-[var(--brand)]" />;
  } else if (type === "error") {
    icon = <AlertCircle className="w-10 h-10 text-[var(--fail)]" />;
  }

  const bgClass = isDarkSurface
    ? "bg-[var(--ev-surface)] text-[var(--ev-text)] border-[var(--ev-line)]"
    : "bg-[var(--doc-surface)] text-[var(--doc-text)] border-[var(--doc-line)]";

  return (
    <div
      className={`flex flex-col items-center justify-center text-center p-8 rounded-[var(--r-md)] border ${bgClass} ${className}`}
    >
      <div className="p-3 rounded-full bg-[var(--brand-subtle)]/20 mb-3">{icon}</div>
      <h3 className="text-base font-semibold tracking-tight">{title}</h3>
      <p
        className={`mt-1.5 text-xs max-w-md ${
          isDarkSurface ? "text-[var(--ev-text-muted)]" : "text-[var(--doc-text-muted)]"
        }`}
      >
        {description}
      </p>
      {actionLabel && onAction && (
        <div className="mt-4">
          <Button
            variant={type === "error" ? "danger" : "primary"}
            size="sm"
            onClick={onAction}
          >
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
