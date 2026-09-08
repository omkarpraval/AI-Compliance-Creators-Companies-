import React from "react";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "dark";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "primary", size = "md", isLoading = false, disabled, children, ...props }, ref) => {
    // Base styles
    const baseStyle =
      "inline-flex items-center justify-center font-medium transition-all duration-[var(--dur-fast)] rounded-[var(--r-sm)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--brand)] focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none cursor-pointer";

    // Size styles
    const sizeStyles = {
      sm: "h-8 px-3 text-xs gap-1.5",
      md: "h-[38px] px-4 text-sm gap-2",
      lg: "h-11 px-5 text-base gap-2.5",
    };

    // Variant styles matching design tokens
    const variantStyles = {
      primary:
        "bg-[var(--brand)] text-white hover:bg-[var(--brand-hover)] active:bg-[var(--brand-press)] shadow-xs",
      secondary:
        "bg-[var(--doc-surface)] text-[var(--doc-text)] border border-[var(--doc-line-strong)] hover:bg-[var(--doc-bg)] active:border-[var(--doc-text-muted)]",
      ghost:
        "bg-transparent text-[var(--doc-text)] hover:bg-[var(--brand-subtle)] hover:text-[var(--brand)]",
      danger:
        "bg-[var(--fail)] text-white hover:opacity-90 active:scale-[0.98]",
      dark:
        "bg-[var(--ev-surface)] text-[var(--ev-text)] border border-[var(--ev-line-strong)] hover:bg-[var(--ev-raised)] hover:border-[var(--brand)]",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseStyle} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-current" />
            <span>Loading...</span>
          </span>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = "Button";
