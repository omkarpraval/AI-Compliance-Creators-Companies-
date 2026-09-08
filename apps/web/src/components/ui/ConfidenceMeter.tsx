import React from "react";

export interface ConfidenceMeterProps {
  confidence: number; // 0.0 to 1.0
  className?: string;
  showText?: boolean;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({
  confidence,
  className = "",
  showText = false,
}) => {
  const percentage = Math.round(Math.min(Math.max(confidence, 0), 1) * 100);
  const activeSegments = Math.ceil(confidence * 4);

  let fillColor = "bg-[var(--pass)]";
  if (confidence < 0.5) {
    fillColor = "bg-[var(--flag)]";
  } else if (confidence < 0.75) {
    fillColor = "bg-[var(--info)]";
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 ${className}`}
      title={`AI Extraction Confidence: ${percentage}%`}
    >
      <div className="flex gap-0.5 w-12 h-1.5 bg-[var(--ev-line-strong)]/40 rounded-[var(--r-xs)] p-[1px]">
        {[1, 2, 3, 4].map((seg) => (
          <div
            key={seg}
            className={`flex-1 rounded-[1px] transition-colors duration-[var(--dur-fast)] ${
              seg <= activeSegments ? fillColor : "bg-transparent"
            }`}
          />
        ))}
      </div>
      {showText && (
        <span className="text-[10px] font-mono-tabular text-[var(--ev-text-muted)]">
          {percentage}%
        </span>
      )}
    </div>
  );
};
