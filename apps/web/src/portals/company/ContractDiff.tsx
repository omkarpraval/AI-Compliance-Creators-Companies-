import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { GitCompare, ArrowLeft, Check, Plus, Minus, RefreshCw } from "lucide-react";
import type { ContractDiff as ContractDiffData } from "@shared/index";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { StateBlock } from "@/components/ui/StateBlock";

export const ContractDiff: React.FC = () => {
  const { id, otherId } = useParams<{ id: string; otherId: string }>();
  const [diffData, setDiffData] = useState<ContractDiffData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadDiff() {
      if (!id || !otherId) return;
      try {
        setIsLoading(true);
        const res = await api.get<ContractDiffData>(`/contracts/${id}/diff/${otherId}`);
        setDiffData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadDiff();
  }, [id, otherId]);

  if (isLoading || !diffData) {
    return (
      <AppLayout>
        <StateBlock type="loading" title="Comparing Revisions..." description="Computing clause-by-clause contract diff..." />
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <PageHeader
        title={`Contract Clause Diff — v${diffData.base_version} vs v${diffData.target_version}`}
        subtitle={diffData.summary}
        actions={
          <Button variant="secondary" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4 mr-1.5" />
            Back to Contract
          </Button>
        }
      />

      {/* Summary Alert Banner */}
      <div className="mb-6 p-4 bg-[var(--doc-surface)] rounded-[var(--r-md)] border-l-4 border-[var(--brand)] shadow-xs flex items-center justify-between text-xs">
        <div className="flex items-center gap-3">
          <GitCompare className="w-5 h-5 text-[var(--brand)]" />
          <span className="text-[var(--doc-text)] font-medium">
            {diffData.summary}
          </span>
        </div>
      </div>

      {/* Two-Column Comparison Grid */}
      <div className="flex flex-col gap-4">
        {diffData.diff_items.map((item, idx) => {
          let bgClass = "bg-[var(--doc-surface)] border-[var(--doc-line)]";
          let badge = null;

          if (item.change_type === "added") {
            bgClass = "bg-[var(--pass-subtle)]/30 border-[var(--pass)]/40";
            badge = (
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[var(--pass)] text-white inline-flex items-center gap-1">
                <Plus className="w-3 h-3" /> ADDED
              </span>
            );
          } else if (item.change_type === "removed") {
            bgClass = "bg-[var(--fail-subtle)]/30 border-[var(--fail)]/40";
            badge = (
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[var(--fail)] text-white inline-flex items-center gap-1">
                <Minus className="w-3 h-3" /> REMOVED
              </span>
            );
          } else if (item.change_type === "modified") {
            bgClass = "bg-purple-50/50 border-purple-300";
            badge = (
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-600 text-white inline-flex items-center gap-1">
                <RefreshCw className="w-3 h-3" /> MODIFIED
              </span>
            );
          }

          return (
            <div
              key={idx}
              className={`p-4 rounded-[var(--r-md)] border ${bgClass} shadow-xs flex flex-col gap-2`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-[var(--brand)]">
                    {item.clause_ref}
                  </span>
                  {badge}
                </div>
                {item.diff_fields && (
                  <span className="text-[10px] font-mono text-[var(--doc-text-muted)]">
                    Changed fields: {item.diff_fields.join(", ")}
                  </span>
                )}
              </div>

              {/* Diff Content View */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                {/* Prior Version v1 */}
                <div className="p-3 bg-white/70 rounded border border-[var(--doc-line)] text-xs">
                  <span className="text-[10px] font-mono font-bold text-[var(--doc-text-faint)] block mb-1">
                    VERSION {diffData.base_version}
                  </span>
                  {item.previous_clause ? (
                    <div>
                      <p className="font-semibold text-[var(--doc-text)]">
                        {item.previous_clause.requirement}
                      </p>
                      <p className="text-[11px] text-[var(--doc-text-muted)] italic mt-1 font-doc">
                        "{item.previous_clause.source_text}"
                      </p>
                    </div>
                  ) : (
                    <span className="text-gray-400 italic">Not present in v{diffData.base_version}</span>
                  )}
                </div>

                {/* Target Version v2 */}
                <div className="p-3 bg-white/70 rounded border border-[var(--doc-line)] text-xs">
                  <span className="text-[10px] font-mono font-bold text-[var(--doc-text-faint)] block mb-1">
                    VERSION {diffData.target_version}
                  </span>
                  {item.current_clause ? (
                    <div>
                      <p className="font-semibold text-[var(--doc-text)]">
                        {item.current_clause.requirement}
                      </p>
                      <p className="text-[11px] text-[var(--doc-text-muted)] italic mt-1 font-doc">
                        "{item.current_clause.source_text}"
                      </p>
                    </div>
                  ) : (
                    <span className="text-gray-400 italic">Removed in v{diffData.target_version}</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </AppLayout>
  );
};
