import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Sparkles,
  AlertCircle,
  FileCheck,
  Clock,
  ArrowRight,
  ShieldCheck,
  DollarSign,
  ChevronRight,
  Upload,
  CheckCircle2,
} from "lucide-react";
import type { Submission, Contract, Campaign } from "@shared/index";
import { api } from "@/lib/api";
import { formatCurrency, formatRelativeTime } from "@/lib/formatters";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { StateBlock } from "@/components/ui/StateBlock";

export const CreatorHome: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadCreatorData() {
      try {
        setIsLoading(true);
        const [subsRes, campsRes] = await Promise.all([
          api.get<{ items: Submission[] }>("/submissions?limit=10"),
          api.get<Campaign[]>("/creators/me/campaigns"),
        ]);
        setSubmissions(subsRes.items || []);
        setCampaigns(campsRes || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadCreatorData();
  }, []);

  const needsAttention = submissions.filter(
    (s) => s.status === "changes_requested" || s.status === "failed"
  );
  const inReview = submissions.filter(
    (s) => s.status === "report_ready" || s.status === "processing" || s.status === "in_review"
  );

  return (
    <AppLayout>
      <PageHeader
        title="Creator Compliance Hub"
        subtitle="Check requirements in plain language, run pre-flight on draft videos, and manage your portable CreatorID™."
        actions={
          <div className="flex items-center gap-3">
            <Button variant="secondary" onClick={() => navigate("/creator/preflight")}>
              <Sparkles className="w-4 h-4 mr-1.5 text-[var(--brand)]" />
              Pre-Flight Check
            </Button>
            <Button variant="primary" onClick={() => navigate("/creator/submit")}>
              <Upload className="w-4 h-4 mr-1.5" />
              Submit Video
            </Button>
          </div>
        }
      />

      {/* Hero Pre-flight Banner (Voluntary Tool CTA) */}
      <div className="p-6 bg-gradient-to-r from-[var(--brand-subtle)]/40 to-white rounded-[var(--r-md)] border border-[var(--brand)]/30 shadow-xs mb-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="px-2.5 py-0.5 rounded-full bg-[var(--brand)] text-white text-[10px] font-mono font-bold uppercase tracking-wider">
            PRE-FLIGHT DRAFT CHECKER
          </span>
          <h2 className="text-base font-bold text-[var(--doc-text)] mt-1.5">
            Test your video before sending to the brand
          </h2>
          <p className="text-xs text-[var(--doc-text-muted)] mt-0.5 max-w-xl">
            Verifyd checks spoken seconds, logo timing, and disclosure tags against your contract and gives you an actionable fix-list. <strong>Nothing is sent to the brand.</strong>
          </p>
        </div>
        <Button variant="primary" size="md" onClick={() => navigate("/creator/preflight")}>
          Run Pre-Flight Check →
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: What Needs Attention */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Action Items List */}
          <div className="p-5 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] shadow-xs">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-[var(--doc-line)]">
              <h3 className="text-sm font-bold text-[var(--doc-text)] flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-[var(--brand)]" />
                What Needs Your Attention
              </h3>
              <span className="text-xs font-mono text-[var(--doc-text-muted)]">
                {needsAttention.length} item(s)
              </span>
            </div>

            {needsAttention.length === 0 ? (
              <div className="py-6 text-center text-xs text-[var(--doc-text-muted)]">
                <CheckCircle2 className="w-8 h-8 text-[var(--pass)] mx-auto mb-2 opacity-80" />
                <span>You're all caught up! No changes requested on your deliverables.</span>
              </div>
            ) : (
              <div className="divide-y divide-[var(--doc-line)]">
                {needsAttention.map((s) => (
                  <div
                    key={s.id}
                    onClick={() => navigate(`/creator/submissions/${s.id}`)}
                    className="py-3 flex items-center justify-between hover:bg-[var(--doc-bg)] p-2 rounded cursor-pointer transition-colors"
                  >
                    <div>
                      <span className="text-xs font-bold text-[var(--fail)]">
                        Fixes requested on {s.campaign_name}
                      </span>
                      <p className="text-[11px] text-[var(--doc-text-muted)]">
                        Contract v{s.contract_version} • Attempt #{s.attempt_number}
                      </p>
                    </div>
                    <Button variant="danger" size="sm">
                      View Fix-List →
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submissions in Review */}
          <div className="p-5 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] shadow-xs">
            <h3 className="text-sm font-bold text-[var(--doc-text)] mb-3 pb-2 border-b border-[var(--doc-line)] flex items-center gap-2">
              <Clock className="w-4 h-4 text-[var(--brand)]" />
              Submissions in Review
            </h3>

            {inReview.length === 0 ? (
              <p className="text-xs text-[var(--doc-text-muted)] py-4">No submissions currently in review.</p>
            ) : (
              <div className="divide-y divide-[var(--doc-line)]">
                {inReview.map((sub) => (
                  <div
                    key={sub.id}
                    onClick={() => navigate(`/creator/submissions/${sub.id}`)}
                    className="py-3 flex items-center justify-between hover:bg-[var(--doc-bg)] p-2 rounded cursor-pointer"
                  >
                    <div>
                      <span className="text-xs font-semibold text-[var(--doc-text)]">
                        {sub.campaign_name || "Campaign"}
                      </span>
                      <p className="text-[11px] text-[var(--doc-text-muted)]">
                        {sub.kind === "preflight" ? "Pre-Flight Draft" : "Final Submission"} •{" "}
                        {formatRelativeTime(sub.submitted_at)}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      {sub.report && <VerdictBadge verdict={sub.report.verdict} size="sm" />}
                      <ChevronRight className="w-4 h-4 text-[var(--doc-text-faint)]" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Pending Earnings & CreatorID Card */}
        <div className="flex flex-col gap-6">
          {/* Earnings Pending Release */}
          <div className="p-5 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] shadow-xs">
            <span className="text-xs uppercase font-mono tracking-wider text-[var(--doc-text-muted)]">
              Earnings Pending Release
            </span>
            <p className="text-3xl font-extrabold text-[var(--doc-text)] mt-1 font-mono-tabular">
              {formatCurrency(85000, "INR")}
            </p>
            <p className="text-[11px] text-[var(--doc-text-muted)] mt-1">
              Released upon brand approval and verified compliance score.
            </p>
          </div>

          {/* Portable CreatorID Card */}
          <div className="p-5 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] shadow-xs flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase font-bold text-[var(--brand)]">
                PORTABLE CREATORID™
              </span>
              <ShieldCheck className="w-4 h-4 text-[var(--pass)]" />
            </div>

            <p className="text-xs text-[var(--doc-text-muted)]">
              Your verified compliance record. Brands check this to fast-track approvals.
            </p>

            <div className="p-3 bg-[var(--doc-bg)] rounded-[var(--r-sm)] border border-[var(--doc-line)] flex items-center justify-between">
              <span className="text-xs font-semibold">Pass Rate:</span>
              <span className="font-mono text-sm font-bold text-[var(--pass)]">94.2%</span>
            </div>

            <Link to="/creator/creatorid">
              <Button variant="secondary" size="sm" className="w-full">
                View Full Credential →
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
