import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Check, Edit2, AlertTriangle, ShieldCheck, FileText, LayoutList } from "lucide-react";
import type { Contract, Clause } from "@shared/index";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import { StateBlock } from "@/components/ui/StateBlock";
import { PdfViewer } from "@/components/pdf/PdfViewer";

export const ContractReview: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [contract, setContract] = useState<Contract | null>(null);
  const [clauses, setClauses] = useState<Clause[]>([]);
  const [selectedClauseId, setSelectedClauseId] = useState<string | null>(null);
  const [editingClauseId, setEditingClauseId] = useState<string | null>(null);
  const [editRequirement, setEditRequirement] = useState("");
  const [editSeverity, setEditSeverity] = useState("standard");
  const [viewMode, setViewMode] = useState<"pdf_canvas" | "serif_text">("pdf_canvas");
  const [isLoading, setIsLoading] = useState(true);
  const [isConfirming, setIsConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadContractClauses() {
      if (!id) return;
      try {
        setIsLoading(true);
        const [cRes, clRes] = await Promise.all([
          api.get<Contract>(`/contracts/${id}`),
          api.get<Clause[]>(`/contracts/${id}/clauses`),
        ]);
        setContract(cRes);
        setClauses(clRes || []);
        if (clRes && clRes.length > 0) {
          setSelectedClauseId(clRes[0].id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadContractClauses();
  }, [id]);

  const handleUpdateClauseStatus = async (clauseId: string, status: "confirmed" | "rejected") => {
    try {
      const updated = await api.patch<Clause>(`/contracts/${id}/clauses/${clauseId}`, {
        review_status: status,
      });
      setClauses((prev) => prev.map((c) => (c.id === clauseId ? updated : c)));
    } catch (err: any) {
      setError(err.message || "Failed to update clause status");
    }
  };

  const handleSaveInlineEdit = async (clauseId: string) => {
    try {
      const updated = await api.patch<Clause>(`/contracts/${id}/clauses/${clauseId}`, {
        requirement: editRequirement,
        severity: editSeverity,
        review_status: "edited",
      });
      setClauses((prev) => prev.map((c) => (c.id === clauseId ? updated : c)));
      setEditingClauseId(null);
    } catch (err: any) {
      setError(err.message || "Failed to save edit");
    }
  };

  const handleConfirmAll = async () => {
    try {
      setIsConfirming(true);
      setError(null);
      await api.post(`/contracts/${id}/confirm`);
      navigate(`/company/campaigns/${contract?.campaign_id}`);
    } catch (err: any) {
      setError(err.message || "Cannot send agreement until all clauses are reviewed.");
    } finally {
      setIsConfirming(false);
    }
  };

  if (isLoading || !contract) {
    return (
      <AppLayout>
        <StateBlock type="loading" title="Loading Checklist..." description="Loading contract document and clauses..." />
      </AppLayout>
    );
  }

  const selectedClause = clauses.find((c) => c.id === selectedClauseId) || clauses[0];
  const unreviewedClauses = clauses.filter((c) => c.review_status === "unreviewed");
  const lowConfidenceClauses = clauses.filter((c) => c.confidence < 0.6);

  const pdfUrl = contract.raw_document_key
    ? `/api/v1/uploads/files/${contract.raw_document_key}`
    : "/sample_contract.pdf";

  return (
    <AppLayout>
      <PageHeader
        title={`Contract Clause Checklist — Version ${contract.version}`}
        subtitle="Verify machine-extracted clauses and inspect exact sentence coordinates before sending agreement to creator."
        actions={
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigate(`/company/campaigns/${contract.campaign_id}`)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleConfirmAll}
              isLoading={isConfirming}
            >
              <ShieldCheck className="w-4 h-4 mr-1.5" />
              Confirm Checklist & Send
            </Button>
          </div>
        }
      />

      {/* Pre-Flag Banner if Low Confidence Clauses Exist */}
      {lowConfidenceClauses.length > 0 && (
        <div className="mb-4 p-3.5 bg-amber-50 border-l-4 border-amber-500 rounded-[var(--r-sm)] flex items-center justify-between text-xs text-amber-900 shadow-xs">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>
              <strong>Check these before sending:</strong> {lowConfidenceClauses.length} clause(s) have subjective wording without explicit thresholds.
            </span>
          </div>
          <span className="font-mono text-[11px] text-amber-700 font-bold">Needs Editorial Approval</span>
        </div>
      )}

      {error && <div className="mb-4 p-3 bg-red-50 text-red-700 text-xs rounded border border-red-200">{error}</div>}

      {/* Split View: Left PDF with Bounding Box Highlights, Right Extracted Checklist */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[640px]">
        {/* Left Pane: PDF Document Viewer / Serif Reading Pane */}
        <div className="lg:col-span-6 flex flex-col min-h-[600px]">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-[var(--doc-line)] text-xs">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-[var(--doc-text)] uppercase text-[11px]">
                SOURCE CONTRACT DOCUMENT
              </span>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setViewMode("pdf_canvas")}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-all ${
                  viewMode === "pdf_canvas"
                    ? "bg-[var(--brand)] text-white"
                    : "bg-transparent text-[var(--doc-text-muted)] hover:text-[var(--doc-text)]"
                }`}
              >
                PDF Page Coordinates
              </button>
              <button
                onClick={() => setViewMode("serif_text")}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-all ${
                  viewMode === "serif_text"
                    ? "bg-[var(--brand)] text-white"
                    : "bg-transparent text-[var(--doc-text-muted)] hover:text-[var(--doc-text)]"
                }`}
              >
                Serif Text View
              </button>
            </div>
          </div>

          {viewMode === "pdf_canvas" ? (
            <PdfViewer
              fileUrl={pdfUrl}
              targetPage={selectedClause?.source_page || (selectedClause?.source_bbox as any)?.page || 1}
              highlightBbox={selectedClause?.source_bbox as any}
              className="flex-1 min-h-[560px]"
            />
          ) : (
            <div className="flex-1 p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] shadow-xs overflow-y-auto max-h-[580px] font-doc text-sm leading-loose text-[var(--doc-text)] space-y-4 pr-2 custom-scrollbar">
              <h4 className="font-bold text-base text-[var(--doc-text)] text-center pb-2">
                INFLUENCER SPONSORSHIP AGREEMENT (v{contract.version})
              </h4>
              <p className="text-xs text-[var(--doc-text-muted)] italic text-center">
                Between Brand Sponsor and Creator (@{contract.creator_handle || "creator"})
              </p>

              {clauses.map((c) => {
                const isHighlighted = selectedClauseId === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => setSelectedClauseId(c.id)}
                    className={`p-2.5 rounded transition-all cursor-pointer ${
                      isHighlighted
                        ? "bg-[var(--brand-subtle)] border-l-3 border-[var(--brand)] font-medium text-[var(--doc-text)] shadow-xs"
                        : "hover:bg-gray-50 border-l-3 border-transparent text-[var(--doc-text-muted)]"
                    }`}
                  >
                    <span className="font-mono text-[10px] font-bold text-[var(--brand)] mr-2 uppercase">
                      [{c.clause_ref}]
                    </span>
                    <span>"{c.source_text}"</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Pane: Extracted Machine-Checkable Checklist */}
        <div className="lg:col-span-6 flex flex-col gap-3">
          <div className="flex items-center justify-between px-4 py-2.5 bg-[var(--doc-surface)] rounded-[var(--r-sm)] border border-[var(--doc-line)]">
            <span className="font-mono text-xs font-semibold text-[var(--doc-text)]">
              EXTRACTED CHECKLIST ({clauses.length} Clauses)
            </span>
            <span className="text-xs text-[var(--doc-text-muted)]">
              {unreviewedClauses.length === 0 ? (
                <span className="text-[var(--pass)] font-medium">✓ All clauses reviewed</span>
              ) : (
                <span>{unreviewedClauses.length} unreviewed</span>
              )}
            </span>
          </div>

          <div className="flex-1 flex flex-col gap-3 overflow-y-auto max-h-[580px] pr-1 custom-scrollbar">
            {clauses.map((clause) => {
              const isSelected = selectedClauseId === clause.id;
              const isEditing = editingClauseId === clause.id;
              const isLowConfidence = clause.confidence < 0.6;
              const pageNum = clause.source_page || (clause.source_bbox as any)?.page || 1;

              return (
                <div
                  key={clause.id}
                  onClick={() => setSelectedClauseId(clause.id)}
                  className={`p-4 rounded-[var(--r-md)] border transition-all ${
                    isSelected
                      ? "bg-[var(--doc-surface)] border-[var(--brand)] shadow-md ring-1 ring-[var(--brand)]/30"
                      : isLowConfidence
                      ? "bg-amber-50/40 border-amber-300 hover:border-amber-400"
                      : "bg-[var(--doc-surface)] border-[var(--doc-line)] hover:border-[var(--doc-line-strong)]"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className="font-mono-tabular text-xs font-bold text-[var(--brand)] px-2 py-0.5 rounded bg-[var(--brand-subtle)]">
                        {clause.clause_ref} · p.{pageNum}
                      </span>
                      <span className="font-mono text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-gray-100 text-gray-700">
                        {clause.clause_type}
                      </span>
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                          clause.severity === "critical"
                            ? "bg-red-50 text-red-700 border border-red-200"
                            : "bg-blue-50 text-blue-700 border border-blue-200"
                        }`}
                      >
                        {clause.severity}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <ConfidenceMeter confidence={clause.confidence} showText />
                      <span
                        className={`text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded ${
                          clause.review_status === "confirmed"
                            ? "bg-[var(--pass-subtle)] text-[var(--pass)]"
                            : clause.review_status === "edited"
                            ? "bg-purple-50 text-purple-700"
                            : "bg-amber-50 text-amber-700"
                        }`}
                      >
                        {clause.review_status}
                      </span>
                    </div>
                  </div>

                  {/* Requirement Text */}
                  {isEditing ? (
                    <div className="mt-3 flex flex-col gap-2">
                      <input
                        type="text"
                        value={editRequirement}
                        onChange={(e) => setEditRequirement(e.target.value)}
                        className="w-full p-2 text-xs bg-[var(--doc-bg)] border border-[var(--brand)] rounded-[var(--r-sm)] text-[var(--doc-text)]"
                      />
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setEditingClauseId(null)}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleSaveInlineEdit(clause.id)}
                        >
                          Save
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <p className="mt-2 text-xs font-semibold text-[var(--doc-text)] leading-relaxed">
                      {clause.requirement}
                    </p>
                  )}

                  {/* Verbatim Source Text */}
                  <p className="mt-1 text-[11px] font-doc text-[var(--doc-text-muted)] italic">
                    "{clause.source_text}"
                  </p>

                  {/* Action Buttons for this clause */}
                  <div className="mt-3 flex items-center justify-between pt-2 border-t border-[var(--doc-line)] text-xs">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingClauseId(clause.id);
                        setEditRequirement(clause.requirement);
                        setEditSeverity(clause.severity);
                      }}
                      className="inline-flex items-center gap-1 text-[var(--doc-text-muted)] hover:text-[var(--brand)] cursor-pointer"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                      <span>Edit Requirement</span>
                    </button>

                    <div className="flex items-center gap-2">
                      <Button
                        variant={clause.review_status === "confirmed" ? "secondary" : "primary"}
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleUpdateClauseStatus(clause.id, "confirmed");
                        }}
                      >
                        <Check className="w-3.5 h-3.5 mr-1" />
                        Confirm
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
