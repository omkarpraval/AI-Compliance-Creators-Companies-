import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { CheckCircle2, Clock, AlertTriangle, ArrowLeft, RefreshCw, Sparkles, FileText } from "lucide-react";
import type { Submission, SubmissionStatus } from "@shared/index";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { EvidenceTimeline } from "@/components/evidence/EvidenceTimeline";
import { StateBlock } from "@/components/ui/StateBlock";

export const CreatorSubmissionStatus: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [statusData, setStatusData] = useState<SubmissionStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const loadData = async () => {
    if (!id) return;
    try {
      const [sub, stat] = await Promise.all([
        api.get<Submission>(`/submissions/${id}`),
        api.get<SubmissionStatus>(`/submissions/${id}/status`),
      ]);
      setSubmission(sub);
      setStatusData(stat);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      if (submission?.status === "processing" || submission?.status === "queued") {
        loadData();
      }
    }, 2500);
    return () => clearInterval(interval);
  }, [id, submission?.status]);

  if (isLoading || !submission) {
    return (
      <AppLayout isDarkWorkspace>
        <StateBlock type="loading" title="Loading Deliverable..." description="Checking pipeline verification status..." isDarkSurface />
      </AppLayout>
    );
  }

  const isComplete = submission.status === "report_ready" || submission.status === "approved" || submission.status === "changes_requested";

  const pipelineStages = [
    "Uploading",
    "Extracting audio",
    "Transcribing",
    "Analysing video",
    "Matching clauses",
    "Building report",
  ];

  return (
    <AppLayout isDarkWorkspace={isComplete}>
      <PageHeader
        title={`Deliverable Audit — Attempt #${submission.attempt_number}`}
        subtitle={`Contract Version ${submission.contract_version} • ${submission.kind === "preflight" ? "Pre-Flight Draft" : "Final Submission"}`}
        isDarkSurface={isComplete}
        actions={
          <Button variant={isComplete ? "dark" : "secondary"} size="sm" onClick={() => navigate("/creator")}>
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Dashboard
          </Button>
        }
      />

      {!isComplete ? (
        /* Determinate Staged Pipeline Progress Card (Section 15 requirement) */
        <div className="max-w-xl mx-auto p-8 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] shadow-md flex flex-col gap-6">
          <div className="text-center">
            <h3 className="text-base font-bold text-[var(--doc-text)]">
              AI Compliance Pipeline Running
            </h3>
            <p className="text-xs text-[var(--doc-text-muted)] mt-1">
              Evaluating audio duration, visual presence, and disclosure tags...
            </p>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex justify-between text-xs font-mono font-semibold">
              <span className="text-[var(--brand)]">{statusData?.stage || "Processing"}</span>
              <span className="text-[var(--doc-text-muted)]">{statusData?.progress || 60}%</span>
            </div>
            <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-[var(--brand)] transition-all duration-500 rounded-full"
                style={{ width: `${statusData?.progress || 60}%` }}
              />
            </div>
          </div>

          <div className="flex flex-col gap-2 pt-4 border-t border-[var(--doc-line)]">
            {pipelineStages.map((st, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <CheckCircle2 className="w-3.5 h-3.5 text-[var(--pass)]" />
                <span className="text-[var(--doc-text)]">{st}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* Complete Report with Evidence Timeline */
        <div className="flex flex-col gap-6">
          {submission.report && (
            <EvidenceTimeline
              submission={submission}
              report={submission.report}
              canOverride={false}
            />
          )}
        </div>
      )}
    </AppLayout>
  );
};
