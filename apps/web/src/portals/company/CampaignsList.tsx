import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Search, Filter } from "lucide-react";
import type { Campaign } from "@shared/index";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/formatters";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { DataTable, type Column } from "@/components/ui/DataTable";

export const CampaignsList: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const navigate = useNavigate();

  useEffect(() => {
    async function loadCampaigns() {
      try {
        setIsLoading(true);
        const res = await api.get<{ items: Campaign[] }>("/campaigns");
        setCampaigns(res.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadCampaigns();
  }, []);

  const filteredCampaigns = campaigns.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.product_name.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === "all" || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const columns: Column<Campaign>[] = [
    {
      key: "name",
      header: "Campaign Name",
      sortable: true,
      render: (c) => (
        <div>
          <span className="font-semibold text-[var(--doc-text)] hover:text-[var(--brand)]">
            {c.name}
          </span>
          <span className="block text-[11px] text-[var(--doc-text-muted)]">{c.product_name}</span>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      sortable: true,
      render: (c) => (
        <span
          className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider ${
            c.status === "active"
              ? "bg-[var(--pass-subtle)] text-[var(--pass)] border border-[var(--pass)]/20"
              : "bg-gray-100 text-gray-600 border border-gray-200"
          }`}
        >
          {c.status}
        </span>
      ),
    },
    {
      key: "contract_count",
      header: "Creators",
      align: "center",
      render: (c) => (
        <span className="font-mono text-xs font-semibold">{c.contract_count || 0} contracted</span>
      ),
    },
    {
      key: "starts_on",
      header: "Timeline",
      render: (c) => (
        <span className="text-xs text-[var(--doc-text-muted)] font-mono">
          {formatDate(c.starts_on)} - {formatDate(c.ends_on)}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (c) => (
        <Button
          variant="secondary"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/company/campaigns/${c.id}`);
          }}
        >
          Manage
        </Button>
      ),
    },
  ];

  return (
    <AppLayout>
      <PageHeader
        title="Campaigns"
        subtitle="Organize influencer contracts, briefs, and video audit compliance by brand campaign."
        actions={
          <Button variant="primary" onClick={() => navigate("/company/campaigns/new")}>
            <Plus className="w-4 h-4 mr-1.5" />
            Create Campaign
          </Button>
        }
      />

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="relative w-full max-w-sm">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--doc-text-faint)]" />
          <input
            type="text"
            placeholder="Search campaigns or products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-[var(--doc-surface)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-[var(--doc-text)] focus:outline-none focus:border-[var(--brand)]"
          />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <Filter className="w-3.5 h-3.5 text-[var(--doc-text-faint)]" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1.5 bg-[var(--doc-surface)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredCampaigns}
        onRowClick={(c) => navigate(`/company/campaigns/${c.id}`)}
        isLoading={isLoading}
        emptyMessage="No campaigns matching your criteria."
      />
    </AppLayout>
  );
};
