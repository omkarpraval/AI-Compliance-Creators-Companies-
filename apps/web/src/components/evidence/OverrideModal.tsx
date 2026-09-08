import React, { useState } from "react";
import { X, ShieldAlert, Check } from "lucide-react";
import type { ClauseVerdict, Verdict } from "@shared/index";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";

export interface OverrideModalProps {
  verdict: ClauseVerdict;
  isOpen: boolean;
  onClose: () => void;
  onSubmitOverride: (verdictId: string, newVerdict: Verdict, reason: string) => Promise<void>;
}

export const OverrideModal: React.FC<OverrideModalProps> = ({
  verdict,
  isOpen,
  onClose,
  onSubmitOverride,
}) => {
  const [selectedVerdict, setSelectedVerdict] = useState<Verdict>(verdict.verdict);
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (reason.trim().length < 20) {
      setError("Please provide a detailed justification (minimum 20 characters) for the audit log.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmitOverride(verdict.id, selectedVerdict, reason);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to record override");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4 animate-in fade-in duration-[var(--dur-fast)]">
      <div className="w-full max-w-lg bg-[var(--ev-surface)] text-[var(--ev-text)] rounded-[var(--r-lg)] border border-[var(--ev-line)] shadow-[var(--sh-modal)] overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--ev-line)] bg-[var(--ev-raised)]">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-[var(--brand)]" />
            <h3 className="font-semibold text-sm tracking-tight">
              Adjudicate AI Verdict — Clause {verdict.clause_ref}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-[var(--ev-text-muted)] hover:text-white hover:bg-[var(--ev-line)] cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-4">
          <div>
            <label className="text-xs font-medium text-[var(--ev-text-muted)]">Current AI Verdict</label>
            <div className="mt-1 flex items-center gap-2">
              <VerdictBadge verdict={verdict.verdict} isDarkSurface />
              <span className="text-xs font-mono-tabular text-[var(--ev-text-faint)]">
                (Confidence: {Math.round(verdict.confidence * 100)}%)
              </span>
            </div>
            <p className="mt-2 p-2 bg-[var(--ev-bg)] rounded-[var(--r-xs)] border border-[var(--ev-line)] text-xs text-[var(--ev-text-muted)]">
              {verdict.rationale}
            </p>
          </div>

          <div>
            <label className="text-xs font-medium text-[var(--ev-text)]">New Adjudicated Verdict</label>
            <div className="grid grid-cols-3 gap-2 mt-1.5">
              {(["pass", "fail", "flagged"] as Verdict[]).map((v) => (
                <button
                  type="button"
                  key={v}
                  onClick={() => setSelectedVerdict(v)}
                  className={`flex items-center justify-center p-2.5 rounded-[var(--r-sm)] border text-xs font-semibold uppercase tracking-wider transition-all cursor-pointer ${
                    selectedVerdict === v
                      ? "border-[var(--brand)] bg-[var(--brand-subtle-d)] text-white shadow-xs"
                      : "border-[var(--ev-line)] bg-[var(--ev-bg)] text-[var(--ev-text-muted)] hover:border-[var(--ev-line-strong)]"
                  }`}
                >
                  {selectedVerdict === v && <Check className="w-3.5 h-3.5 mr-1.5 text-[var(--brand)]" />}
                  {v}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-[var(--ev-text)] flex justify-between">
              <span>Required Justification Note (Audit Log)</span>
              <span className="text-[10px] font-mono-tabular text-[var(--ev-text-faint)]">
                {reason.length}/20 min chars
              </span>
            </label>
            <textarea
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="State explicit reason for changing verdict (e.g. 'Spoken duration verified through manual frame count; competitor logo was background poster not sponsor...')"
              className="mt-1.5 w-full p-2.5 rounded-[var(--r-sm)] bg-[var(--ev-bg)] border border-[var(--ev-line)] text-xs text-[var(--ev-text)] placeholder-[var(--ev-text-faint)] focus:outline-none focus:border-[var(--brand)]"
            />
          </div>

          {error && <p className="text-xs text-[var(--fail)]">{error}</p>}

          <div className="flex justify-end gap-2.5 pt-3 border-t border-[var(--ev-line)]">
            <Button variant="dark" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={isSubmitting}>
              Save Override & Audit
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
