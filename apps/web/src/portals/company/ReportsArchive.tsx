import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Download, Search, Filter, FileText } from "lucide-react";
import type { Submission } from "@shared/index";
import { api } from "@/lib/api";
import { formatDate, formatRelativeTime } from "@/lib/formatters";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { DataTable, type Column } from "@/components/ui/DataTable";

export const ReportsArchive: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function loadReports() {
      try {
        setIsLoading(true);
        const res = await api.get<{ items: Submission[] }>("/submissions?limit=50");
        setSubmissions(res.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadReports();
  }, []);

  const filtered = submissions.filter(
    (s) =>
      (s.campaign_name?.toLowerCase().includes(search.toLowerCase()) ||
        s.creator_handle?.toLowerCase().includes(search.toLowerCase())) &&
      s.report != null
  );

  const columns: Column<Submission>[] = [
    {
      key: "deliverable",
      header: "Deliverable & Campaign",
      render: (s) => (
        <div>
          <span className="font-semibold text-[var(--doc-text)]">{s.campaign_name}</span>
          <span className="block text-[11px] text-[var(--doc-text-muted)] font-mono">
            @{s.creator_handle || "creator"} • Contract v{s.contract_version}
          </span>
        </div>
      ),
    },
    {
      key: "verdict",
      header: "Verdict",
      render: (s) => s.report ? <VerdictBadge verdict={s.report.verdict} size="sm" /> : <span>—</span>,
    },
    {
      key: "score",
      header: "Score",
      render: (s) => (
        <span className="font-mono text-xs font-bold text-[var(--doc-text)]">
          {s.report?.overall_score}%
        </span>
      ),
    },
    {
      key: "passed_failed",
      header: "Passed / Flagged / Failed",
      render: (s) =>
        s.report ? (
          <span className="text-xs font-mono text-[var(--doc-text-muted)]">
            <span className="text-[var(--pass)] font-bold">{s.report.clauses_passed}</span> /{" "}
            <span className="text-[var(--flag)] font-bold">{s.report.clauses_flagged}</span> /{" "}
            <span className="text-[var(--fail)] font-bold">{s.report.clauses_failed}</span>
          </span>
        ) : (
          <span>—</span>
        ),
    },
    {
      key: "submitted_at",
      header: "Audit Date",
      render: (s) => <span className="text-xs text-[var(--doc-text-muted)]">{formatDate(s.submitted_at)}</span>,
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (s) => (
        <div className="flex items-center justify-end gap-2">
          <a
            href={`/api/v1/submissions/${s.id}/report/export`}
            target="_blank"
            rel="noreferrer"
            className="p-1.5 rounded text-[var(--doc-text-muted)] hover:text-[var(--brand)] hover:bg-[var(--doc-bg)] cursor-pointer"
            title="Download PDF"
            onClick={(e) => e.stopPropagation()}
          >
            <Download className="w-4 h-4" />
          </a>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => navigate(`/company/submissions/${s.id}/review`)}
          >
            View Evidence
          </Button>
        </div>
      ),
    },
  ];

  return (
    <AppLayout>
      <PageHeader
        title="Compliance Reports Archive"
        subtitle="Complete audit trail of all AI-evaluated creator videos with clause-by-clause timestamped evidence."
      />

      <div className="flex items-center justify-between gap-4 mb-4">
        <div className="relative w-full max-w-sm">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--doc-text-faint)]" />
          <input
            type="text"
            placeholder="Search campaign, creator..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-[var(--doc-surface)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-[var(--doc-text)] focus:outline-none focus:border-[var(--brand)]"
          />
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filtered}
        onRowClick={(s) => navigate(`/company/submissions/${s.id}/review`)}
        isLoading={isLoading}
        emptyMessage="No compliance reports found."
      />
    </AppLayout>
  );
};
