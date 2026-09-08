import React, { useRef, useEffect } from "react";
import type { EvidenceItem } from "@shared/index";
import { formatTimecode } from "@/lib/formatters";

export interface TranscriptStripProps {
  currentTime: number;
  activeEvidence: EvidenceItem | null;
  onSeek: (seconds: number) => void;
  className?: string;
}

export const TranscriptStrip: React.FC<TranscriptStripProps> = ({
  currentTime,
  activeEvidence,
  onSeek,
  className = "",
}) => {
  const activeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
    }
  }, [currentTime]);

  const transcriptText =
    activeEvidence?.type === "transcript_span"
      ? activeEvidence.payload?.text
      : "Hey everyone, welcome back to my channel! Today is sponsored by Lumen Skincare. I have been testing their new Hydration Serum over the last two weeks, and it honestly gave me that glass-skin glow without feeling greasy. Make sure you check out Lumen Skincare with the link in my bio for 20% off your first bottle!";

  return (
    <div
      className={`w-full p-3 bg-[var(--ev-surface)] rounded-[var(--r-md)] border border-[var(--ev-line)] text-xs leading-relaxed ${className}`}
    >
      <div className="flex items-center justify-between mb-1.5 text-[10px] font-mono-tabular text-[var(--ev-text-faint)]">
        <span>SYNCHRONIZED TRANSCRIPT</span>
        {activeEvidence?.type === "transcript_span" && (
          <span className="text-[var(--brand)] font-semibold">
            Anchor: {formatTimecode(activeEvidence.start_ms / 1000)} - {formatTimecode(activeEvidence.end_ms / 1000)}
          </span>
        )}
      </div>

      <div className="p-2.5 bg-[var(--ev-bg)] rounded-[var(--r-xs)] border border-[var(--ev-line)]/50 text-[var(--ev-text)] overflow-x-auto custom-scrollbar">
        <p className="font-mono text-xs leading-relaxed text-[var(--ev-text)]">
          <span className="p-1 rounded bg-[var(--brand-subtle-d)] text-[var(--brand-hover)] border border-[var(--brand)]/40 font-medium">
            "{transcriptText}"
          </span>
        </p>
      </div>
    </div>
  );
};
