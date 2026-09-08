import React, { useState, useEffect } from "react";
import { Sparkles, Shield, AlertTriangle, CheckCircle2, ArrowRight, Play, Eye } from "lucide-react";
import type { Contract, Submission } from "@shared/index";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { FileDropzone } from "@/components/ui/FileDropzone";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { EvidenceTimeline } from "@/components/evidence/EvidenceTimeline";

export const PreflightCheck: React.FC = () => {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContractId, setSelectedContractId] = useState<string>("");
  const [videoFileKey, setVideoFileKey] = useState<string | null>(null);
  const [captionText, setCaptionText] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [pipelineStage, setPipelineStage] = useState("Uploading");
  const [submissionResult, setSubmissionResult] = useState<Submission | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadContracts() {
      try {
        const res = await api.get<{ items: Contract[] }>("/contracts/1/clauses"); // fallback or load active contracts
        const cRes = await api.get<{ items: Contract[] }>("/campaigns/1/contracts").catch(() => null);
        if (cRes?.items && cRes.items.length > 0) {
          setContracts(cRes.items);
          setSelectedContractId(cRes.items[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    }
    loadContracts();
  }, []);

  const handleRunPreflight = async () => {
    if (!videoFileKey) {
      setError("Please select or upload a draft video to run pre-flight check.");
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      setPipelineStage("Transcribing audio & measuring duration...");

      // Simulate realistic staged pipeline progress
      await new Promise((r) => setTimeout(r, 600));
      setPipelineStage("Multimodal visual analysis & logo timing...");
      await new Promise((r) => setTimeout(r, 600));
      setPipelineStage("Matching against contract clauses...");

      const res = await api.post<Submission>("/submissions", {
        contract_id: selectedContractId || "sample-contract",
        kind: "preflight",
        video_file_key: videoFileKey,
        caption_text: captionText,
        duration_seconds: 30.0,
      });

      setSubmissionResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to process pre-flight check");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <AppLayout isDarkWorkspace={submissionResult != null}>
      <PageHeader
        title="Pre-Flight Draft Check"
        subtitle="Self-audit your draft video against contract obligations before publishing or sending to the brand."
        isDarkSurface={submissionResult != null}
      />

      {/* Prominent Safety Assurance Banner (Section 14 requirement) */}
      <div className="mb-6 p-4 bg-emerald-50 border-l-4 border-[var(--pass)] rounded-[var(--r-sm)] flex items-center justify-between text-xs text-emerald-950 shadow-xs">
        <div className="flex items-center gap-3">
          <Shield className="w-5 h-5 text-[var(--pass)] shrink-0" />
          <span>
            <strong>Private Workspace:</strong> This draft check is 100% private to you. <strong>This does not submit anything to the brand.</strong>
          </span>
        </div>
      </div>

      {!submissionResult ? (
        <div className="max-w-2xl mx-auto flex flex-col gap-6">
          {/* Upload and Configuration Card */}
          <div className="p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] flex flex-col gap-4 shadow-xs">
            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">
                Select Brand Campaign Contract
              </label>
              <select
                value={selectedContractId}
                onChange={(e) => setSelectedContractId(e.target.value)}
                className="w-full p-2.5 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
              >
                <option value="contract-alex-v2">Hydration Serum Global Launch (Contract v2)</option>
                <option value="contract-maya-v1">Luxe Cleanse Autumn Campaign (Contract v1)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">
                Draft Video File
              </label>
              <FileDropzone
                accept="video/mp4,video/quicktime"
                label="Drop your draft video here (MP4 / MOV)"
                hint="Verifyd will analyze speech duration, logo timing, and disclosure tags."
                onFileUploaded={(key) => setVideoFileKey(key)}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">
                Planned Post Caption (Optional)
              </label>
              <textarea
                rows={2}
                value={captionText}
                onChange={(e) => setCaptionText(e.target.value)}
                placeholder="Include your planned caption text with hashtags (#ad, @brand)..."
                className="w-full p-2.5 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
              />
            </div>

            {error && <p className="text-xs text-[var(--fail)]">{error}</p>}

            {isProcessing && (
              <div className="p-4 bg-[var(--brand-subtle)] rounded-[var(--r-sm)] flex items-center justify-between text-xs text-[var(--brand)] font-medium animate-pulse">
                <span>{pipelineStage}</span>
                <span className="font-mono">Processing...</span>
              </div>
            )}

            <div className="flex justify-end pt-3">
              <Button
                variant="primary"
                size="lg"
                onClick={handleRunPreflight}
                isLoading={isProcessing}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Run Pre-Flight Analysis
              </Button>
            </div>
          </div>
        </div>
      ) : (
        /* Actionable Fix-List + Read-Only Evidence Timeline */
        <div className="flex flex-col gap-6">
          {/* Actionable Fix-List Card */}
          <div className="p-6 bg-[var(--ev-surface)] rounded-[var(--r-md)] border border-[var(--ev-line)] text-[var(--ev-text)]">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--ev-line)]">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-[var(--flag)]" />
                <h3 className="text-sm font-bold">Actionable Fix-List (Pre-Flight Results)</h3>
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={() => setSubmissionResult(null)}
              >
                Test Another Draft
              </Button>
            </div>

            <div className="mt-4 flex flex-col gap-2.5">
              {submissionResult.report?.verdicts
                .filter((v) => v.verdict !== "pass")
                .map((v) => (
                  <div
                    key={v.id}
                    className="p-3 bg-[var(--ev-bg)] rounded-[var(--r-xs)] border border-[var(--flag)]/40 flex items-start justify-between gap-3 text-xs"
                  >
                    <div>
                      <span className="font-mono font-bold text-[var(--brand)] mr-2">[{v.clause_ref}]</span>
                      <span className="text-[var(--ev-text)]">{v.rationale}</span>
                    </div>
                    <VerdictBadge verdict={v.verdict} isDarkSurface size="sm" />
                  </div>
                ))}

              {submissionResult.report?.verdicts.filter((v) => v.verdict !== "pass").length === 0 && (
                <div className="py-4 text-center text-xs text-[var(--pass)] font-medium flex items-center justify-center gap-2">
                  <CheckCircle2 className="w-5 h-5" />
                  <span>All clauses passed! Your video is 100% compliant and ready to submit.</span>
                </div>
              )}
            </div>
          </div>

          {/* Interactive Evidence Timeline */}
          {submissionResult.report && (
            <EvidenceTimeline
              submission={submissionResult}
              report={submissionResult.report}
              canOverride={false}
            />
          )}
        </div>
      )}
    </AppLayout>
  );
};
