import React from "react";

export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
  isDarkSurface?: boolean;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  badge,
  actions,
  className = "",
  isDarkSurface = false,
}) => {
  return (
    <div className={`flex flex-wrap items-center justify-between gap-4 pb-6 ${className}`}>
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-3">
          <h1
            className={`text-2xl font-bold tracking-tight ${
              isDarkSurface ? "text-[var(--ev-text)]" : "text-[var(--doc-text)]"
            }`}
          >
            {title}
          </h1>
          {badge}
        </div>
        {subtitle && (
          <p
            className={`text-xs ${
              isDarkSurface ? "text-[var(--ev-text-muted)]" : "text-[var(--doc-text-muted)]"
            }`}
          >
            {subtitle}
          </p>
        )}
      </div>

      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  );
};
