import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, ArrowRight, Clock, CheckCircle2, AlertCircle, FileText, ChevronRight } from "lucide-react";
import type { Submission, Campaign } from "@shared/index";
import { api } from "@/lib/api";
import { formatRelativeTime, formatDate } from "@/lib/formatters";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { StateBlock } from "@/components/ui/StateBlock";

export const CompanyDashboard: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setIsLoading(true);
        const [subsRes, campsRes] = await Promise.all([
          api.get<{ items: Submission[] }>("/submissions?limit=10"),
          api.get<{ items: Campaign[] }>("/campaigns?limit=5"),
        ]);
        setSubmissions(subsRes.items || []);
        setCampaigns(campsRes.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const pendingSubmissions = submissions.filter(
    (s) => s.status === "report_ready" || s.status === "in_review" || s.status === "processing"
  );

  return (
    <AppLayout>
      <PageHeader
        title="Brand Compliance Overview"
        subtitle="Manage active campaigns, review extracted contract checklists, and audit delivered creator videos."
        actions={
          <Button variant="primary" onClick={() => navigate("/company/campaigns/new")}>
            <Plus className="w-4 h-4 mr-1.5" />
            New Campaign
          </Button>
        }
      />

      {isLoading ? (
        <StateBlock type="loading" title="Loading Dashboard..." description="Fetching active campaigns and pending submissions..." />
      ) : (
        <div className="flex flex-col gap-8">
          {/* Primary Action Panel: Awaiting Your Review (Section 14 requirement) */}
          <div className="p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <Clock className="w-5 h-5 text-[var(--brand)]" />
                <h2 className="text-base font-bold text-[var(--doc-text)]">Awaiting Your Review</h2>
                <span className="px-2 py-0.5 rounded-full bg-[var(--brand-subtle)] text-[var(--brand)] text-xs font-mono font-bold">
                  {pendingSubmissions.length}
                </span>
              </div>
              <Link to="/company/reports" className="text-xs text-[var(--brand)] hover:underline font-medium">
                View All Submissions →
              </Link>
            </div>

            {pendingSubmissions.length === 0 ? (
              <p className="text-xs text-[var(--doc-text-muted)] py-4">
                No submissions currently waiting for review. New video deliverables will appear here automatically.
              </p>
            ) : (
              <div className="divide-y divide-[var(--doc-line)]">
                {pendingSubmissions.map((sub) => (
                  <div
                    key={sub.id}
                    onClick={() => navigate(`/company/submissions/${sub.id}/review`)}
                    className="py-3.5 flex items-center justify-between hover:bg-[var(--doc-bg)]/80 p-3 rounded-[var(--r-sm)] transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-[var(--r-sm)] bg-[var(--brand-subtle)] flex items-center justify-center text-[var(--brand)] font-bold text-sm">
                        v{sub.contract_version}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-[var(--doc-text)]">
                            @{sub.creator_handle || "creator"}
                          </span>
                          <span className="text-xs text-[var(--doc-text-muted)]">• {sub.campaign_name}</span>
                        </div>
                        <p className="text-[11px] text-[var(--doc-text-faint)] mt-0.5">
                          Submitted {formatRelativeTime(sub.submitted_at)} • Attempt #{sub.attempt_number}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      {sub.report && (
                        <div className="text-right">
                          <span className="text-[10px] uppercase font-mono tracking-wider text-[var(--doc-text-faint)] block">
                            Score
                          </span>
                          <span className="font-mono text-sm font-bold text-[var(--doc-text)]">
                            {sub.report.overall_score}%
                          </span>
                        </div>
                      )}
                      {sub.report ? (
                        <VerdictBadge verdict={sub.report.verdict} />
                      ) : (
                        <span className="text-xs font-mono px-2 py-1 bg-amber-50 text-amber-700 rounded border border-amber-200">
                          {sub.status.toUpperCase()}
                        </span>
                      )}
                      <ChevronRight className="w-4 h-4 text-[var(--doc-text-faint)]" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Secondary Metric Strip: Active Campaigns & Turnaround */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)]">
              <span className="text-xs text-[var(--doc-text-muted)] uppercase tracking-wider font-mono">
                Active Campaigns
              </span>
              <p className="text-3xl font-extrabold text-[var(--doc-text)] mt-1 font-mono-tabular">
                {campaigns.filter((c) => c.status === "active").length}
              </p>
              <Link to="/company/campaigns" className="text-xs text-[var(--brand)] hover:underline mt-2 inline-block">
                View all campaigns →
              </Link>
            </div>

            <div className="p-5 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)]">
              <span className="text-xs text-[var(--doc-text-muted)] uppercase tracking-wider font-mono">
                Pass Rate (This Month)
              </span>
              <p className="text-3xl font-extrabold text-[var(--pass)] mt-1 font-mono-tabular">
                92.4%
              </p>
              <span className="text-xs text-[var(--doc-text-muted)] mt-1 block">
                Based on 18 creator video audits
              </span>
            </div>

            <div className="p-5 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)]">
              <span className="text-xs text-[var(--doc-text-muted)] uppercase tracking-wider font-mono">
                Average Review Turnaround
              </span>
              <p className="text-3xl font-extrabold text-[var(--doc-text)] mt-1 font-mono-tabular">
                1.2 hrs
              </p>
              <span className="text-xs text-[var(--doc-text-muted)] mt-1 block">
                Automated pre-adjudication enabled
              </span>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
};
