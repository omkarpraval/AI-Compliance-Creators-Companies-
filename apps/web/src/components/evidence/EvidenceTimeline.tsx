import React, { useState, useEffect, useCallback } from "react";
import {
  HelpCircle,
  SlidersHorizontal,
  ArrowUpDown,
  Download,
  Share2,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";
import type { ComplianceReport, Submission, ClauseVerdict, Verdict, EvidenceItem } from "@shared/index";
import { formatTimecode, formatDurationMs } from "@/lib/formatters";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { ClauseRow } from "@/components/ui/ClauseRow";
import { VideoStage } from "./VideoStage";
import { MultiTrackTimeline } from "./MultiTrackTimeline";
import { TranscriptStrip } from "./TranscriptStrip";
import { OverrideModal } from "./OverrideModal";
import { KeyboardShortcutModal } from "./KeyboardShortcutModal";
import { api } from "@/lib/api";

export interface EvidenceTimelineProps {
  submission: Submission;
  report: ComplianceReport;
  videoUrl?: string;
  canOverride?: boolean;
  onRefresh?: () => void;
  className?: string;
}

export const EvidenceTimeline: React.FC<EvidenceTimelineProps> = ({
  submission,
  report,
  videoUrl = "",
  canOverride = false,
  onRefresh,
  className = "",
}) => {
  const [selectedVerdictId, setSelectedVerdictId] = useState<string | null>(
    report.verdicts[0]?.id || null
  );
  const [sortBy, setSortBy] = useState<"severity" | "contract">("severity");
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(submission.duration_seconds || 30.0);
  const [isOverrideOpen, setIsOverrideOpen] = useState(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);

  // Animated score counter for report reveal
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    // Reveal count up animation
    const target = report.overall_score;
    let start = 0;
    const step = Math.max(1, Math.floor(target / 30));
    const interval = setInterval(() => {
      start += step;
      if (start >= target) {
        setDisplayScore(target);
        clearInterval(interval);
      } else {
        setDisplayScore(start);
      }
    }, 28);
    return () => clearInterval(interval);
  }, [report.overall_score]);

  // Sort clauses: fails first, then flagged, then passes
  const sortedVerdicts = [...report.verdicts].sort((a, b) => {
    if (sortBy === "contract") {
      return a.clause_ref.localeCompare(b.clause_ref);
    }
    const order: Record<string, number> = { fail: 1, flagged: 2, pass: 3 };
    return (order[a.verdict] || 4) - (order[b.verdict] || 4);
  });

  const selectedVerdict =
    report.verdicts.find((v) => v.id === selectedVerdictId) || report.verdicts[0];

  // Active evidence based on current timestamp
  const activeEvidence =
    selectedVerdict?.evidence_items?.find(
      (ev) => currentTime * 1000 >= ev.start_ms - 200 && currentTime * 1000 <= ev.end_ms + 200
    ) ||
    selectedVerdict?.evidence_items?.[0] ||
    null;

  // Scrub handler to smoothly seek video player
  const handleSelectClause = useCallback(
    (verdictId: string) => {
      setSelectedVerdictId(verdictId);
      const v = report.verdicts.find((item) => item.id === verdictId);
      if (v && v.evidence_items && v.evidence_items.length > 0) {
        const firstEv = v.evidence_items[0];
        const targetSec = firstEv.start_ms / 1000;
        setCurrentTime(targetSec);
      }
    },
    [report.verdicts]
  );

  // Keyboard navigation shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (["input", "textarea"].includes((e.target as HTMLElement)?.tagName?.toLowerCase())) return;

      if (e.code === "Space") {
        e.preventDefault();
        setIsPlaying((prev) => !prev);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        setCurrentTime((prev) => Math.max(0, prev - (e.shiftKey ? 0.05 : 5)));
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        setCurrentTime((prev) => Math.min(duration, prev + (e.shiftKey ? 0.05 : 5)));
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        const curIdx = sortedVerdicts.findIndex((v) => v.id === selectedVerdictId);
        if (curIdx < sortedVerdicts.length - 1) {
          handleSelectClause(sortedVerdicts[curIdx + 1].id);
        }
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        const curIdx = sortedVerdicts.findIndex((v) => v.id === selectedVerdictId);
        if (curIdx > 0) {
          handleSelectClause(sortedVerdicts[curIdx - 1].id);
        }
      } else if (e.key.toLowerCase() === "o" && canOverride) {
        e.preventDefault();
        setIsOverrideOpen(true);
      } else if (e.key === "?") {
        e.preventDefault();
        setIsShortcutsOpen((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [sortedVerdicts, selectedVerdictId, duration, canOverride, handleSelectClause]);

  const handleOverrideSubmit = async (verdictId: string, newVerdict: Verdict, reason: string) => {
    await api.patch(`/verdicts/${verdictId}/override`, { verdict: newVerdict, reason });
    if (onRefresh) onRefresh();
  };

  const resolvedVideoUrl =
    videoUrl ||
    (submission.video_file_key
      ? `/api/v1/uploads/files/${submission.video_file_key}`
      : "/api/v1/uploads/files/sample_skincare_review.mp4");

  return (
    <div
      className={`w-full flex flex-col bg-[var(--ev-bg)] text-[var(--ev-text)] rounded-[var(--r-lg)] border border-[var(--ev-line)] shadow-xl overflow-hidden select-none ${className}`}
    >
      {/* Evidence Room Dark Header */}
      <div className="flex flex-wrap items-center justify-between px-6 py-4 bg-[var(--ev-surface)] border-b border-[var(--ev-line)] gap-4">
        <div className="flex items-center gap-4">
          <div className="flex flex-col">
            <span className="text-[10px] uppercase font-mono-tabular tracking-wider text-[var(--brand)] font-semibold">
              EVIDENCE ROOM • ATTEMPT #{submission.attempt_number}
            </span>
            <h2 className="text-base font-bold text-[var(--ev-text)]">
              {submission.creator_handle ? `@${submission.creator_handle}` : "Creator"} • {submission.campaign_name || "Campaign Compliance Audit"}
            </h2>
          </div>
        </div>

        {/* Score Stamp & Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-3 px-3.5 py-1.5 bg-[var(--ev-raised)] rounded-[var(--r-md)] border border-[var(--ev-line)]">
            <div className="flex flex-col text-right">
              <span className="text-[9px] font-mono-tabular uppercase tracking-wider text-[var(--ev-text-muted)]">
                Score
              </span>
              <span className="font-mono-tabular text-xl font-extrabold text-[var(--brand-hover)]">
                {displayScore}%
              </span>
            </div>
            <div className="h-7 w-[1px] bg-[var(--ev-line)]" />
            <VerdictBadge verdict={report.verdict} isDarkSurface size="lg" />
          </div>

          <button
            onClick={() => setIsShortcutsOpen(true)}
            className="p-2 text-[var(--ev-text-muted)] hover:text-white hover:bg-[var(--ev-raised)] rounded-[var(--r-sm)] border border-[var(--ev-line)] cursor-pointer"
            title="Keyboard Shortcuts (?)"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Evidence Workspace Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[580px]">
        {/* Left: Clause Rail (360px / col-4) */}
        <div className="lg:col-span-4 flex flex-col bg-[var(--ev-surface)] border-r border-[var(--ev-line)] overflow-hidden">
          {/* Rail Header & Sorter */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-[var(--ev-raised)] border-b border-[var(--ev-line)]">
            <span className="text-xs font-semibold text-[var(--ev-text-muted)] uppercase tracking-wider font-mono-tabular">
              Contract Clauses ({report.verdicts.length})
            </span>
            <button
              onClick={() => setSortBy(sortBy === "severity" ? "contract" : "severity")}
              className="inline-flex items-center gap-1 text-xs text-[var(--brand)] hover:underline cursor-pointer"
            >
              <ArrowUpDown className="w-3.5 h-3.5" />
              <span>{sortBy === "severity" ? "Severity" : "Contract Order"}</span>
            </button>
          </div>

          {/* Clause Row List */}
          <div className="flex-1 p-3 flex flex-col gap-2 overflow-y-auto max-h-[440px] custom-scrollbar">
            {sortedVerdicts.map((v) => (
              <ClauseRow
                key={v.id}
                clauseRef={v.clause_ref}
                requirement={v.rationale}
                verdict={v.verdict}
                confidence={v.confidence}
                isSelected={selectedVerdictId === v.id}
                isOverridden={v.is_overridden}
                overrideVerdict={v.override_verdict}
                onClick={() => handleSelectClause(v.id)}
                isDarkSurface
              />
            ))}
          </div>

          {/* Selected Clause Rationale Panel */}
          {selectedVerdict && (
            <div className="p-4 bg-[var(--ev-raised)] border-t border-[var(--ev-line)] flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono-tabular font-bold text-[var(--brand)]">
                  {selectedVerdict.clause_ref} AUDIT RATIONALE
                </span>
                {canOverride && (
                  <Button
                    variant="dark"
                    size="sm"
                    onClick={() => setIsOverrideOpen(true)}
                    className="h-6 text-[11px] px-2 text-[var(--brand)]"
                  >
                    Adjudicate (O)
                  </Button>
                )}
              </div>
              <p className="text-xs leading-relaxed text-[var(--ev-text)]">
                {selectedVerdict.rationale}
              </p>

              {/* Measured vs Required Tabular Mono Metrics */}
              <div className="mt-1 p-2 bg-[var(--ev-bg)] rounded-[var(--r-xs)] border border-[var(--ev-line)] font-mono-tabular text-[11px] flex justify-between text-[var(--ev-text-muted)]">
                <span>
                  Measured:{" "}
                  <strong className="text-[var(--brand-hover)]">
                    {JSON.stringify(selectedVerdict.measured_value)}
                  </strong>
                </span>
                <span>
                  Req:{" "}
                  <strong className="text-[var(--ev-text)]">
                    {JSON.stringify(selectedVerdict.required_value)}
                  </strong>
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Right: Video Stage + Multi-Track Timeline (col-8) */}
        <div className="lg:col-span-8 flex flex-col p-4 bg-[var(--ev-bg)] gap-3">
          {/* 16:9 Video Canvas */}
          <VideoStage
            videoUrl={resolvedVideoUrl}
            isPlaying={isPlaying}
            currentTime={currentTime}
            duration={duration}
            activeEvidence={activeEvidence}
            onPlayPause={() => setIsPlaying(!isPlaying)}
            onSeek={(t) => setCurrentTime(t)}
            onDurationChange={(d) => setDuration(d)}
            onTimeUpdate={(t) => setCurrentTime(t)}
          />

          {/* Multi-Track Timeline with Audio Waveform */}
          <MultiTrackTimeline
            verdicts={report.verdicts}
            selectedVerdictId={selectedVerdictId}
            currentTime={currentTime}
            duration={duration}
            onSeek={(t) => setCurrentTime(t)}
            onSelectClause={(id) => handleSelectClause(id)}
          />

          {/* Synchronized Transcript Strip */}
          <TranscriptStrip
            currentTime={currentTime}
            activeEvidence={activeEvidence}
            onSeek={(t) => setCurrentTime(t)}
          />
        </div>
      </div>

      {/* Override Dialog */}
      {selectedVerdict && (
        <OverrideModal
          verdict={selectedVerdict}
          isOpen={isOverrideOpen}
          onClose={() => setIsOverrideOpen(false)}
          onSubmitOverride={handleOverrideSubmit}
        />
      )}

      {/* Keyboard Shortcuts Sheet */}
      <KeyboardShortcutModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />
    </div>
  );
};
