import React, { useEffect, useState } from "react";
import { Activity, RefreshCw, CheckCircle2, XCircle, Clock, AlertTriangle } from "lucide-react";
import type { Job } from "@shared/index";
import { api } from "@/lib/api";
import { formatRelativeTime } from "@/lib/formatters";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { DataTable, type Column } from "@/components/ui/DataTable";

export const PipelineHealth: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [retryingJobId, setRetryingJobId] = useState<string | null>(null);

  const loadJobs = async () => {
    try {
      setIsLoading(true);
      const res = await api.get<{ items: Job[] }>("/admin/jobs");
      setJobs(res.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handleRetry = async (jobId: string) => {
    try {
      setRetryingJobId(jobId);
      await api.post(`/admin/jobs/${jobId}/retry`);
      await loadJobs();
    } catch (err) {
      console.error(err);
    } finally {
      setRetryingJobId(null);
    }
  };

  const columns: Column<Job>[] = [
    {
      key: "task_name",
      header: "Pipeline Task",
      render: (j) => (
        <div>
          <span className="font-mono text-xs font-bold text-[var(--ev-text)]">{j.task_name}</span>
          <span className="block text-[10px] text-[var(--ev-text-muted)] font-mono">
            ID: {j.id.slice(0, 8)} • Attempt {j.attempt}/{j.max_attempts}
          </span>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (j) => (
        <span
          className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
            j.status === "succeeded"
              ? "bg-[var(--pass-dark)] text-[var(--pass)] border border-[var(--pass)]/30"
              : j.status === "failed"
              ? "bg-[var(--fail-dark)] text-[var(--fail)] border border-[var(--fail)]/30"
              : "bg-blue-950 text-blue-400 border border-blue-800"
          }`}
        >
          {j.status}
        </span>
      ),
    },
    {
      key: "error",
      header: "Error Detail",
      render: (j) =>
        j.error_message ? (
          <span className="text-xs text-[var(--fail)] font-mono truncate max-w-xs block">
            {j.error_class}: {j.error_message}
          </span>
        ) : (
          <span className="text-xs text-[var(--ev-text-faint)] font-mono">None</span>
        ),
    },
    {
      key: "created_at",
      header: "Timestamp",
      render: (j) => (
        <span className="text-xs font-mono text-[var(--ev-text-muted)]">
          {formatRelativeTime(j.created_at)}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (j) => (
        <Button
          variant="dark"
          size="sm"
          onClick={() => handleRetry(j.id)}
          isLoading={retryingJobId === j.id}
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1 text-[var(--brand)]" />
          Retry Task
        </Button>
      ),
    },
  ];

  return (
    <AppLayout isDarkWorkspace>
      <PageHeader
        title="Pipeline Health & Task Observability"
        subtitle="Real-time monitoring of Celery tasks across transcription, visual analysis, and report generation."
        isDarkSurface
        actions={
          <Button variant="dark" size="sm" onClick={loadJobs}>
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Refresh
          </Button>
        }
      />

      {/* Stacked Status Distribution Summary (Section 14 requirement) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="p-4 bg-[var(--ev-surface)] rounded-[var(--r-md)] border border-[var(--ev-line)]">
          <span className="text-xs font-mono text-[var(--ev-text-muted)]">SUCCEEDED</span>
          <p className="text-2xl font-bold font-mono text-[var(--pass)] mt-1">
            {jobs.filter((j) => j.status === "succeeded").length}
          </p>
        </div>
        <div className="p-4 bg-[var(--ev-surface)] rounded-[var(--r-md)] border border-[var(--ev-line)]">
          <span className="text-xs font-mono text-[var(--ev-text-muted)]">RUNNING</span>
          <p className="text-2xl font-bold font-mono text-blue-400 mt-1">
            {jobs.filter((j) => j.status === "running").length}
          </p>
        </div>
        <div className="p-4 bg-[var(--ev-surface)] rounded-[var(--r-md)] border border-[var(--ev-line)]">
          <span className="text-xs font-mono text-[var(--ev-text-muted)]">QUEUED</span>
          <p className="text-2xl font-bold font-mono text-amber-400 mt-1">
            {jobs.filter((j) => j.status === "queued").length}
          </p>
        </div>
        <div className="p-4 bg-[var(--ev-surface)] rounded-[var(--r-md)] border border-[var(--ev-line)]">
          <span className="text-xs font-mono text-[var(--ev-text-muted)]">FAILED</span>
          <p className="text-2xl font-bold font-mono text-[var(--fail)] mt-1">
            {jobs.filter((j) => j.status === "failed").length}
          </p>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={jobs}
        isLoading={isLoading}
        emptyMessage="No pipeline jobs recorded."
        isDarkSurface
      />
    </AppLayout>
  );
};
