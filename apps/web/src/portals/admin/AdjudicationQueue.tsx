import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldAlert, ArrowRight, CheckCircle2, Clock, Filter } from "lucide-react";
import type { Submission } from "@shared/index";
import { api } from "@/lib/api";
import { formatRelativeTime } from "@/lib/formatters";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { VerdictBadge } from "@/components/ui/VerdictBadge";
import { DataTable, type Column } from "@/components/ui/DataTable";

export const AdjudicationQueue: React.FC = () => {
  const [queue, setQueue] = useState<Submission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadQueue() {
      try {
        setIsLoading(true);
        const res = await api.get<{ items: Submission[] }>("/admin/queue");
        setQueue(res.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadQueue();
  }, []);

  const columns: Column<Submission>[] = [
    {
      key: "deliverable",
      header: "Deliverable & Campaign",
      render: (s) => (
        <div>
          <span className="font-semibold text-[var(--ev-text)]">{s.campaign_name}</span>
          <span className="block text-[11px] text-[var(--ev-text-muted)] font-mono">
            @{s.creator_handle || "creator"} • Attempt #{s.attempt_number}
          </span>
        </div>
      ),
    },
    {
      key: "flagged_count",
      header: "Flagged Clauses",
      render: (s) => (
        <span className="px-2 py-0.5 rounded bg-[var(--flag-dark)] text-[var(--flag)] border border-[var(--flag)]/30 font-mono text-xs font-bold">
          {s.report?.clauses_flagged || 1} Needs Human Adjudication
        </span>
      ),
    },
    {
      key: "overall_score",
      header: "AI Score",
      render: (s) => (
        <span className="font-mono text-xs font-bold text-[var(--ev-text)]">
          {s.report?.overall_score}%
        </span>
      ),
    },
    {
      key: "submitted_at",
      header: "Waiting Since",
      render: (s) => (
        <span className="text-xs text-[var(--ev-text-muted)] font-mono">
          {formatRelativeTime(s.submitted_at)}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (s) => (
        <Button
          variant="primary"
          size="sm"
          onClick={() => navigate(`/company/submissions/${s.id}/review`)}
        >
          Adjudicate Evidence →
        </Button>
      ),
    },
  ];

  return (
    <AppLayout isDarkWorkspace>
      <PageHeader
        title="Flagged Clauses Adjudication Queue"
        subtitle="Review ambiguous clauses where confidence fell below 0.75 or arithmetic checks flagged a mismatch. Oldest first."
        isDarkSurface
      />

      <div className="flex flex-col gap-4">
        <DataTable
          columns={columns}
          data={queue}
          onRowClick={(s) => navigate(`/company/submissions/${s.id}/review`)}
          isLoading={isLoading}
          emptyMessage="Zero flagged clauses in queue! All submissions have been resolved."
          isDarkSurface
        />
      </div>
    </AppLayout>
  );
};
