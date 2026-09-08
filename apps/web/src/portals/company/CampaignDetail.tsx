import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Plus, FileText, ArrowRight, GitCompare, CheckCircle2, AlertCircle, Shield, Upload } from "lucide-react";
import type { Campaign, Contract, Submission } from "@shared/index";
import { api } from "@/lib/api";
import { formatCurrency, formatDate, formatRelativeTime } from "@/lib/formatters";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { DataTable, type Column } from "@/components/ui/DataTable";
import { StateBlock } from "@/components/ui/StateBlock";

export const CampaignDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [activeTab, setActiveTab] = useState<"creators" | "submissions" | "settings">("creators");
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadCampaignData() {
      if (!id) return;
      try {
        setIsLoading(true);
        const [cRes, ctRes, sRes] = await Promise.all([
          api.get<Campaign>(`/campaigns/${id}`),
          api.get<{ items: Contract[] }>(`/campaigns/${id}/contracts`),
          api.get<{ items: Submission[] }>(`/submissions?campaign_id=${id}`),
        ]);
        setCampaign(cRes);
        setContracts(ctRes.items || []);
        setSubmissions(sRes.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadCampaignData();
  }, [id]);

  if (isLoading || !campaign) {
    return (
      <AppLayout>
        <StateBlock type="loading" title="Loading Campaign..." description="Fetching campaign details and contract versions..." />
      </AppLayout>
    );
  }

  const contractColumns: Column<Contract>[] = [
    {
      key: "creator",
      header: "Creator",
      render: (ct) => (
        <div>
          <span className="font-semibold text-[var(--doc-text)]">
            @{ct.creator_handle || "alexrivers"}
          </span>
          <span className="block text-[11px] text-[var(--doc-text-muted)] font-mono">
            Version {ct.version}
          </span>
        </div>
      ),
    },
    {
      key: "status",
      header: "Contract Status",
      render: (ct) => (
        <span
          className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase ${
            ct.status === "signed"
              ? "bg-[var(--pass-subtle)] text-[var(--pass)]"
              : ct.status === "needs_review"
              ? "bg-[var(--flag-subtle)] text-[var(--flag)] border border-[var(--flag)]/30"
              : "bg-gray-100 text-gray-700"
          }`}
        >
          {ct.status.replace("_", " ")}
        </span>
      ),
    },
    {
      key: "fee_amount",
      header: "Contract Value",
      render: (ct) => (
        <span className="font-mono text-xs font-semibold text-[var(--doc-text)]">
          {formatCurrency(ct.fee_amount, ct.fee_currency)}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (ct) => (
        <div className="flex items-center justify-end gap-2">
          {ct.parent_contract_id && (
            <Button
              variant="secondary"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/company/contracts/${ct.id}/diff/${ct.parent_contract_id}`);
              }}
              title="View Clause Diff against previous version"
            >
              <GitCompare className="w-3.5 h-3.5 mr-1 text-[var(--brand)]" />
              Diff v{ct.version - 1}
            </Button>
          )}

          <Button
            variant={ct.status === "needs_review" ? "primary" : "secondary"}
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/company/contracts/${ct.id}/review`);
            }}
          >
            {ct.status === "needs_review" ? "Review Checklist" : "Inspect Clauses"}
          </Button>
        </div>
      ),
    },
  ];

  const submissionColumns: Column<Submission>[] = [
    {
      key: "creator",
      header: "Deliverable",
      render: (s) => (
        <div>
          <span className="font-semibold text-[var(--doc-text)]">@{s.creator_handle || "creator"}</span>
          <span className="block text-[11px] text-[var(--doc-text-muted)] font-mono">
            Attempt #{s.attempt_number} • Contract v{s.contract_version}
          </span>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (s) => (
        <span
          className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase ${
            s.status === "approved"
              ? "bg-[var(--pass-subtle)] text-[var(--pass)]"
              : s.status === "changes_requested"
              ? "bg-[var(--fail-subtle)] text-[var(--fail)]"
              : "bg-blue-50 text-blue-700"
          }`}
        >
          {s.status.replace("_", " ")}
        </span>
      ),
    },
    {
      key: "report",
      header: "Compliance Score",
      render: (s) =>
        s.report ? (
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-bold text-[var(--doc-text)]">
              {s.report.overall_score}%
            </span>
            <VerdictBadge verdict={s.report.verdict} size="sm" />
          </div>
        ) : (
          <span className="text-xs text-[var(--doc-text-muted)] font-mono">Processing...</span>
        ),
    },
    {
      key: "submitted_at",
      header: "Submitted",
      render: (s) => <span className="text-xs text-[var(--doc-text-muted)]">{formatRelativeTime(s.submitted_at)}</span>,
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (s) => (
        <Button
          variant="secondary"
          size="sm"
          onClick={() => navigate(`/company/submissions/${s.id}/review`)}
        >
          Audit Timeline →
        </Button>
      ),
    },
  ];

  return (
    <AppLayout>
      <PageHeader
        title={campaign.name}
        subtitle={`Product: ${campaign.product_name} • ${formatDate(campaign.starts_on)} to ${formatDate(campaign.ends_on)}`}
        badge={
          <span
            className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold uppercase ${
              campaign.status === "active"
                ? "bg-[var(--pass-subtle)] text-[var(--pass)]"
                : "bg-gray-100 text-gray-700"
            }`}
          >
            {campaign.status}
          </span>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={() => navigate("/company/campaigns")}>
              ← All Campaigns
            </Button>
          </div>
        }
      />

      {/* Tabs */}
      <div className="flex items-center gap-6 border-b border-[var(--doc-line)] mb-6">
        <button
          onClick={() => setActiveTab("creators")}
          className={`pb-3 text-xs font-semibold cursor-pointer transition-all border-b-2 ${
            activeTab === "creators"
              ? "border-[var(--brand)] text-[var(--brand)]"
              : "border-transparent text-[var(--doc-text-muted)] hover:text-[var(--doc-text)]"
          }`}
        >
          Creators & Contracts ({contracts.length})
        </button>
        <button
          onClick={() => setActiveTab("submissions")}
          className={`pb-3 text-xs font-semibold cursor-pointer transition-all border-b-2 ${
            activeTab === "submissions"
              ? "border-[var(--brand)] text-[var(--brand)]"
              : "border-transparent text-[var(--doc-text-muted)] hover:text-[var(--doc-text)]"
          }`}
        >
          Deliverables & Audits ({submissions.length})
        </button>
      </div>

      {activeTab === "creators" && (
        <div className="flex flex-col gap-4">
          <div className="flex justify-between items-center">
            <p className="text-xs text-[var(--doc-text-muted)]">
              All creator agreements governing deliverables for this campaign.
            </p>
          </div>
          <DataTable columns={contractColumns} data={contracts} />
        </div>
      )}

      {activeTab === "submissions" && (
        <div className="flex flex-col gap-4">
          <DataTable columns={submissionColumns} data={submissions} />
        </div>
      )}
    </AppLayout>
  );
};
