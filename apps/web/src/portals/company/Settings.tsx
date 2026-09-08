import React from "react";
import { Sliders, Building, Users, Shield, Bell } from "lucide-react";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";

export const CompanySettings: React.FC = () => {
  return (
    <AppLayout>
      <PageHeader
        title="Organization Settings"
        subtitle="Manage brand profile, team member permissions, notifications, and connected e-sign providers."
      />

      <div className="max-w-3xl flex flex-col gap-6">
        {/* Organization Profile */}
        <div className="p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] flex flex-col gap-4">
          <div className="flex items-center gap-2 pb-2 border-b border-[var(--doc-line)]">
            <Building className="w-5 h-5 text-[var(--brand)]" />
            <h3 className="text-sm font-bold text-[var(--doc-text)]">Brand Profile</h3>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">Organization Name</label>
              <input
                type="text"
                defaultValue="Lumen Skincare"
                className="w-full p-2 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">Country / Jurisdiction</label>
              <input
                type="text"
                defaultValue="India (IN)"
                className="w-full p-2 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
              />
            </div>
          </div>
        </div>

        {/* E-sign & Contract Integrations */}
        <div className="p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] flex flex-col gap-4">
          <div className="flex items-center gap-2 pb-2 border-b border-[var(--doc-line)]">
            <Shield className="w-5 h-5 text-[var(--brand)]" />
            <h3 className="text-sm font-bold text-[var(--doc-text)]">Connected E-Sign & Storage</h3>
          </div>

          <div className="flex items-center justify-between p-3 bg-[var(--doc-bg)] rounded-[var(--r-sm)] border border-[var(--doc-line)] text-xs">
            <div>
              <span className="font-semibold text-[var(--doc-text)]">DocuSign / Leegality E-Sign Provider</span>
              <p className="text-[11px] text-[var(--doc-text-muted)]">Active • Envelope auto-routing enabled</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--pass-subtle)] text-[var(--pass)] font-bold">
              CONNECTED
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-[var(--doc-bg)] rounded-[var(--r-sm)] border border-[var(--doc-line)] text-xs">
            <div>
              <span className="font-semibold text-[var(--doc-text)]">MinIO / S3 Media Storage</span>
              <p className="text-[11px] text-[var(--doc-text-muted)]">Presigned direct uploads enabled</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--pass-subtle)] text-[var(--pass)] font-bold">
              ACTIVE
            </span>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
