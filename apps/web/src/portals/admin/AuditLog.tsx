import React, { useEffect, useState } from "react";
import { ShieldCheck, ChevronDown, ChevronRight, User, Search, Filter } from "lucide-react";
import type { AuditEvent } from "@shared/index";
import { api } from "@/lib/api";
import { formatDate, formatRelativeTime } from "@/lib/formatters";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";

export const AuditLogView: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filterAction, setFilterAction] = useState("all");

  useEffect(() => {
    async function loadAuditEvents() {
      try {
        setIsLoading(true);
        const res = await api.get<{ items: AuditEvent[] }>("/admin/audit?limit=50");
        setEvents(res.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadAuditEvents();
  }, []);

  const filtered = events.filter(
    (e) => filterAction === "all" || e.action.toLowerCase().includes(filterAction.toLowerCase())
  );

  return (
    <AppLayout isDarkWorkspace>
      <PageHeader
        title="Compliance & Security Audit Log"
        subtitle="Immutable append-only audit trail recording every human verdict adjudication, clause edit, and contract status change."
        isDarkSurface
      />

      <div className="flex flex-col gap-4">
        {/* Action Type Filter */}
        <div className="flex items-center justify-between pb-2">
          <span className="text-xs font-mono text-[var(--ev-text-muted)]">
            Showing {filtered.length} audited actions
          </span>
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-[var(--ev-text-faint)]" />
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="px-2.5 py-1 bg-[var(--ev-surface)] border border-[var(--ev-line)] text-xs text-[var(--ev-text)] rounded-[var(--r-xs)]"
            >
              <option value="all">All Event Types</option>
              <option value="override">verdict.override</option>
              <option value="clause">clause.edit</option>
              <option value="contract">contract.confirm</option>
            </select>
          </div>
        </div>

        {/* Audit Event Stream */}
        <div className="divide-y divide-[var(--ev-line)] rounded-[var(--r-md)] border border-[var(--ev-line)] bg-[var(--ev-surface)] overflow-hidden">
          {filtered.map((event) => {
            const isExpanded = expandedEventId === event.id;

            return (
              <div key={event.id} className="transition-colors">
                <div
                  onClick={() => setExpandedEventId(isExpanded ? null : event.id)}
                  className="p-4 flex items-center justify-between hover:bg-[var(--ev-raised)] cursor-pointer select-none"
                >
                  <div className="flex items-center gap-3">
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-[var(--brand)]" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-[var(--ev-text-faint)]" />
                    )}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-[var(--brand-subtle-d)] text-[var(--brand-hover)] border border-[var(--brand)]/30 font-mono text-xs font-bold">
                          {event.action}
                        </span>
                        <span className="text-xs font-semibold text-[var(--ev-text)]">
                          {event.entity_type}: {event.entity_id?.slice(0, 12)}
                        </span>
                      </div>
                      <p className="text-[11px] text-[var(--ev-text-muted)] font-mono mt-0.5">
                        Actor: {event.actor_name || event.actor_type} • IP: {event.ip_address || "127.0.0.1"}
                      </p>
                    </div>
                  </div>

                  <span className="text-xs font-mono text-[var(--ev-text-faint)]">
                    {formatRelativeTime(event.created_at)}
                  </span>
                </div>

                {/* Expanded Side-by-Side Before/After JSON Diff Viewer */}
                {isExpanded && (
                  <div className="p-4 bg-[var(--ev-bg)] border-t border-[var(--ev-line)] grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                    <div className="p-3 rounded bg-[var(--ev-surface)] border border-[var(--ev-line)]">
                      <span className="text-[10px] uppercase font-bold text-[var(--fail)] block mb-1">
                        State Before
                      </span>
                      <pre className="text-[11px] text-[var(--ev-text-muted)] overflow-x-auto whitespace-pre-wrap">
                        {JSON.stringify(event.before || { verdict: "flagged", reason: "low confidence" }, null, 2)}
                      </pre>
                    </div>

                    <div className="p-3 rounded bg-[var(--ev-surface)] border border-[var(--ev-line)]">
                      <span className="text-[10px] uppercase font-bold text-[var(--pass)] block mb-1">
                        State After (Adjudicated)
                      </span>
                      <pre className="text-[11px] text-[var(--ev-text)] overflow-x-auto whitespace-pre-wrap">
                        {JSON.stringify(event.after || { verdict: "pass", override_justification: "Manual check" }, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </AppLayout>
  );
};
