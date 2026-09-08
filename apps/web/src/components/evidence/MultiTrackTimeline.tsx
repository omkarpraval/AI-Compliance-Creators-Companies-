import React, { useRef } from "react";
import type { ClauseVerdict, EvidenceItem } from "@shared/index";
import { formatTimecode } from "@/lib/formatters";
import { AudioWaveform } from "./AudioWaveform";

export interface MultiTrackTimelineProps {
  verdicts: ClauseVerdict[];
  selectedVerdictId: string | null;
  currentTime: number;
  duration: number;
  onSeek: (seconds: number) => void;
  onSelectClause: (verdictId: string) => void;
}

export const MultiTrackTimeline: React.FC<MultiTrackTimelineProps> = ({
  verdicts,
  selectedVerdictId,
  currentTime,
  duration,
  onSeek,
  onSelectClause,
}) => {
  const timelineRef = useRef<HTMLDivElement>(null);

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current || duration <= 0) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const pct = Math.max(0, Math.min(1, clickX / rect.width));
    onSeek(pct * duration);
  };

  // Only render tracks that have evidence items
  const tracks = verdicts.filter((v) => v.evidence_items && v.evidence_items.length > 0);

  // Time markers (5 evenly spaced intervals)
  const timeMarkers = [0, 0.25, 0.5, 0.75, 1.0].map((pct) => ({
    pct: pct * 100,
    time: formatTimecode(pct * duration),
  }));

  const playheadPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="w-full flex flex-col gap-2 p-3 bg-[var(--ev-surface)] rounded-[var(--r-md)] border border-[var(--ev-line)] select-none">
      {/* Waveform Track */}
      <div className="flex items-center gap-3">
        <span className="w-12 text-[10px] font-mono-tabular text-[var(--ev-text-faint)] text-right">
          AUDIO
        </span>
        <div className="flex-1">
          <AudioWaveform currentTime={currentTime} duration={duration} onSeek={onSeek} />
        </div>
      </div>

      {/* Multi-Track Container */}
      <div
        ref={timelineRef}
        onClick={handleTimelineClick}
        className="relative flex-1 flex flex-col gap-1.5 py-2 cursor-pointer"
      >
        {/* Playhead Line */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-[var(--brand)] z-20 pointer-events-none transition-all duration-[var(--dur-instant)]"
          style={{ left: `${playheadPercent}%` }}
        >
          <div className="w-2.5 h-2.5 -ml-1 -top-1 absolute bg-[var(--brand)] rounded-full shadow-xs ring-2 ring-white/50" />
        </div>

        {/* Clause Tracks */}
        {tracks.map((v) => {
          const isSelected = selectedVerdictId === v.id;
          const trackOpacity = selectedVerdictId == null || isSelected ? "opacity-100" : "opacity-25";

          // Track color based on verdict
          let segmentBg = "bg-[var(--pass)]";
          if (v.verdict === "fail") segmentBg = "bg-[var(--fail)]";
          else if (v.verdict === "flagged") segmentBg = "bg-[var(--flag)]";

          return (
            <div
              key={v.id}
              onClick={(e) => {
                e.stopPropagation();
                onSelectClause(v.id);
              }}
              className={`flex items-center gap-3 transition-opacity duration-[var(--dur-fast)] ${trackOpacity}`}
            >
              <span
                className={`w-12 text-[11px] font-mono-tabular font-semibold text-right ${
                  isSelected ? "text-[var(--brand)]" : "text-[var(--ev-text-muted)]"
                }`}
              >
                {v.clause_ref}
              </span>

              {/* Track Lane */}
              <div className="flex-1 relative h-5 bg-[var(--ev-bg)] rounded-[var(--r-xs)] border border-[var(--ev-line)]/60 overflow-hidden">
                {v.evidence_items.map((ev, idx) => {
                  const startPct = duration > 0 ? (ev.start_ms / 1000 / duration) * 100 : 0;
                  const endPct = duration > 0 ? (ev.end_ms / 1000 / duration) * 100 : 100;
                  const widthPct = Math.max(2, endPct - startPct);

                  return (
                    <div
                      key={ev.id || idx}
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectClause(v.id);
                        onSeek(ev.start_ms / 1000);
                      }}
                      className={`absolute top-0.5 bottom-0.5 rounded-[var(--r-xs)] ${segmentBg} opacity-75 hover:opacity-100 transition-all hover:scale-y-110 shadow-xs cursor-pointer`}
                      style={{
                        left: `${startPct}%`,
                        width: `${widthPct}%`,
                      }}
                      title={`${v.clause_ref} [${ev.type}]: ${formatTimecode(ev.start_ms / 1000)} - ${formatTimecode(
                        ev.end_ms / 1000
                      )}`}
                    />
                  );
                })}
              </div>
            </div>
          );
        })}

        {/* Timecode Grid Marks */}
        <div className="relative w-full h-4 mt-1 border-t border-[var(--ev-line)]">
          {timeMarkers.map((marker, i) => (
            <span
              key={i}
              className="absolute top-1 text-[9px] font-mono-tabular text-[var(--ev-text-faint)] -translate-x-1/2"
              style={{ left: `${marker.pct}%` }}
            >
              {marker.time}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
