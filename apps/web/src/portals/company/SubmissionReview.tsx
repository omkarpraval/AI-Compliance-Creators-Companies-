import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { CheckCircle2, XCircle, AlertCircle, ArrowLeft, Download, RefreshCw } from "lucide-react";
import type { Submission } from "@shared/index";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { EvidenceTimeline } from "@/components/evidence/EvidenceTimeline";
import { StateBlock } from "@/components/ui/StateBlock";

export const SubmissionReview: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false);
  const [decisionNote, setDecisionNote] = useState("");
  const [showChangesModal, setShowChangesModal] = useState(false);
  const navigate = useNavigate();

  const loadSubmission = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      const res = await api.get<Submission>(`/submissions/${id}`);
      setSubmission(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSubmission();
  }, [id]);

  const handleDecision = async (decision: "approved" | "rejected" | "changes_requested") => {
    if (!id) return;
    try {
      setIsSubmittingDecision(true);
      await api.post(`/submissions/${id}/review`, {
        decision,
        note: decisionNote,
      });
      await loadSubmission();
      setShowChangesModal(false);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmittingDecision(false);
    }
  };

  if (isLoading || !submission) {
    return (
      <AppLayout isDarkWorkspace>
        <StateBlock type="loading" title="Loading Submission Review..." description="Fetching video compliance audit and evidence timeline..." isDarkSurface />
      </AppLayout>
    );
  }

  return (
    <AppLayout isDarkWorkspace>
      <PageHeader
        title={`Video Deliverable Review — Attempt #${submission.attempt_number}`}
        subtitle={`Governing Contract: Version ${submission.contract_version} • Creator: @${submission.creator_handle || "alexrivers"}`}
        isDarkSurface
        actions={
          <div className="flex items-center gap-3">
            <Button
              variant="dark"
              size="sm"
              onClick={() => navigate(-1)}
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back
            </Button>
            <a
              href={`/api/v1/submissions/${submission.id}/report/export`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--r-sm)] text-xs font-medium bg-[var(--ev-surface)] text-[var(--ev-text)] border border-[var(--ev-line)] hover:bg-[var(--ev-raised)]"
            >
              <Download className="w-3.5 h-3.5 text-[var(--brand)]" />
              Export PDF Audit
            </a>
          </div>
        }
      />

      {/* Signature Evidence Timeline (Dark Surface) */}
      {submission.report ? (
        <div className="flex flex-col gap-6">
          <EvidenceTimeline
            submission={submission}
            report={submission.report}
            canOverride={true}
            onRefresh={loadSubmission}
          />

          {/* Review Decision Action Bar */}
          <div className="p-6 bg-[var(--ev-surface)] rounded-[var(--r-md)] border border-[var(--ev-line)] flex flex-wrap items-center justify-between gap-4">
            <div>
              <h4 className="text-sm font-bold text-[var(--ev-text)]">Brand Final Review Decision</h4>
              <p className="text-xs text-[var(--ev-text-muted)] mt-0.5">
                Current deliverable status: <span className="uppercase font-mono text-[var(--brand-hover)] font-bold">{submission.status}</span>
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="danger"
                size="md"
                onClick={() => handleDecision("rejected")}
                isLoading={isSubmittingDecision}
              >
                <XCircle className="w-4 h-4 mr-1.5" />
                Reject Deliverable
              </Button>

              <Button
                variant="dark"
                size="md"
                onClick={() => setShowChangesModal(true)}
              >
                <RefreshCw className="w-4 h-4 mr-1.5 text-[var(--flag)]" />
                Request Fixes
              </Button>

              <Button
                variant="primary"
                size="md"
                onClick={() => handleDecision("approved")}
                isLoading={isSubmittingDecision}
                className="bg-[var(--pass)] hover:bg-emerald-600"
              >
                <CheckCircle2 className="w-4 h-4 mr-1.5" />
                Approve & Release Payment
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <StateBlock
          type="empty"
          title="Audit in Progress"
          description="The AI pipeline is currently transcribing and evaluating this video against the contract checklist."
          isDarkSurface
        />
      )}

      {/* Changes Request Dialog */}
      {showChangesModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
          <div className="w-full max-w-md bg-[var(--ev-surface)] text-[var(--ev-text)] rounded-[var(--r-lg)] border border-[var(--ev-line)] p-6 flex flex-col gap-4">
            <h3 className="text-sm font-bold">Request Changes from Creator</h3>
            <p className="text-xs text-[var(--ev-text-muted)]">
              This will create a creator fix-list with timestamps linking directly into their pre-flight workspace.
            </p>
            <textarea
              rows={3}
              value={decisionNote}
              onChange={(e) => setDecisionNote(e.target.value)}
              placeholder="e.g. Please extend product demonstration by 5 seconds and include clear #ad tag at start..."
              className="w-full p-2.5 rounded-[var(--r-sm)] bg-[var(--ev-bg)] border border-[var(--ev-line)] text-xs text-[var(--ev-text)] focus:outline-none focus:border-[var(--brand)]"
            />
            <div className="flex justify-end gap-2">
              <Button variant="dark" size="sm" onClick={() => setShowChangesModal(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleDecision("changes_requested")}
                isLoading={isSubmittingDecision}
              >
                Send Fix-List to Creator
              </Button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
};
