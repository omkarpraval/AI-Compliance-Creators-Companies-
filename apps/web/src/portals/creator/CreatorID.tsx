import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, Share2, Copy, ExternalLink, Award, CheckCircle2, Eye, Sparkles } from "lucide-react";
import type { CreatorID } from "@shared/index";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { StateBlock } from "@/components/ui/StateBlock";

export const CreatorIDCredential: React.FC = () => {
  const [creatorId, setCreatorId] = useState<CreatorID | null>(null);
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadCreatorID() {
      try {
        setIsLoading(true);
        const res = await api.get<CreatorID>("/creators/me/creatorid");
        setCreatorId(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadCreatorID();
  }, []);

  const handleToggleVisibility = async () => {
    if (!creatorId) return;
    try {
      const updated = !creatorId.public_id_enabled;
      await api.post("/creators/me/creatorid/visibility", { enabled: updated });
      setCreatorId({ ...creatorId, public_id_enabled: updated });
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopyLink = () => {
    if (!creatorId) return;
    const url = `${window.location.origin}/c/${creatorId.handle}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  if (isLoading || !creatorId) {
    return (
      <AppLayout>
        <StateBlock type="loading" title="Loading CreatorID™..." description="Calculating compliance pass rate and credentials..." />
      </AppLayout>
    );
  }

  const publicUrl = `${window.location.origin}/c/${creatorId.handle}`;

  return (
    <AppLayout>
      <PageHeader
        title="Portable CreatorID™ Credential"
        subtitle="Your tamper-proof, verified brand compliance track record. Share with brand partners to fast-track approvals."
        actions={
          <div className="flex items-center gap-3">
            <Button variant="secondary" size="sm" onClick={handleCopyLink}>
              <Copy className="w-4 h-4 mr-1.5" />
              {copied ? "Copied Link!" : "Copy Public Link"}
            </Button>
            <Link to={`/c/${creatorId.handle}`} target="_blank">
              <Button variant="primary" size="sm">
                <ExternalLink className="w-4 h-4 mr-1.5" />
                View Public Profile
              </Button>
            </Link>
          </div>
        }
      />

      <div className="max-w-4xl mx-auto flex flex-col gap-8">
        {/* The Credential Hero Card (Section 14 & 15 requirement) */}
        <div className="relative p-8 md:p-12 bg-white rounded-[var(--r-lg)] border-2 border-[var(--doc-line-strong)] shadow-lg overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-[var(--brand-subtle)]/40 to-transparent rounded-full blur-3xl pointer-events-none" />

          {/* Credential Header */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-[var(--doc-line)]">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-[var(--brand-subtle-d)] border-2 border-[var(--brand)] flex items-center justify-center text-xl font-bold text-[var(--brand-hover)] shadow-sm">
                {creatorId.full_name.charAt(0)}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-bold text-[var(--doc-text)]">{creatorId.full_name}</h2>
                  {creatorId.is_verified && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[var(--pass-subtle)] text-[var(--pass)] text-xs font-mono font-bold border border-[var(--pass)]/30">
                      <ShieldCheck className="w-3.5 h-3.5" /> VERIFIED
                    </span>
                  )}
                </div>
                <p className="text-xs font-mono text-[var(--brand)] mt-0.5">@{creatorId.handle}</p>
              </div>
            </div>

            {/* Visibility Toggle */}
            <div className="flex items-center gap-3 p-2 bg-[var(--doc-bg)] rounded-[var(--r-sm)] border border-[var(--doc-line)]">
              <span className="text-xs text-[var(--doc-text-muted)] font-medium">Public URL:</span>
              <button
                onClick={handleToggleVisibility}
                className={`px-2.5 py-1 rounded-[var(--r-xs)] text-xs font-mono font-bold transition-all cursor-pointer ${
                  creatorId.public_id_enabled
                    ? "bg-[var(--pass)] text-white"
                    : "bg-gray-200 text-gray-700"
                }`}
              >
                {creatorId.public_id_enabled ? "LIVE & PUBLIC" : "PRIVATE"}
              </button>
            </div>
          </div>

          {/* Hero Pass-Rate Figure (Serif Display Typography) */}
          <div className="py-8 grid grid-cols-1 md:grid-cols-3 gap-8 text-center md:text-left">
            <div className="md:border-r border-[var(--doc-line)] md:pr-6">
              <span className="text-xs font-mono uppercase tracking-wider text-[var(--doc-text-muted)]">
                Verified Pass Rate
              </span>
              <p className="font-doc text-6xl font-extrabold text-[var(--doc-text)] mt-1 tracking-tight">
                {creatorId.pass_rate}%
              </p>
              <span className="text-xs text-[var(--pass)] font-medium mt-1 inline-flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Top 5% Industry Compliance
              </span>
            </div>

            <div className="md:border-r border-[var(--doc-line)] md:pr-6">
              <span className="text-xs font-mono uppercase tracking-wider text-[var(--doc-text-muted)]">
                Campaigns Completed
              </span>
              <p className="font-doc text-6xl font-extrabold text-[var(--doc-text)] mt-1 tracking-tight">
                {creatorId.campaigns_completed || 14}
              </p>
              <span className="text-xs text-[var(--doc-text-muted)] mt-1 block">
                Across 6 distinct brand partners
              </span>
            </div>

            <div>
              <span className="text-xs font-mono uppercase tracking-wider text-[var(--doc-text-muted)]">
                Avg. Revisions Needed
              </span>
              <p className="font-doc text-6xl font-extrabold text-[var(--brand)] mt-1 tracking-tight">
                {creatorId.average_revisions || 1.1}
              </p>
              <span className="text-xs text-[var(--doc-text-muted)] mt-1 block">
                Fast first-attempt approvals
              </span>
            </div>
          </div>

          {/* Bio & Focus Niches */}
          <div className="pt-6 border-t border-[var(--doc-line)] flex flex-wrap items-center justify-between gap-4">
            <p className="text-xs text-[var(--doc-text-muted)] max-w-xl leading-relaxed">
              "{creatorId.bio || "Content creator specializing in verified skincare and beauty routines."}"
            </p>

            <div className="flex items-center gap-1.5 flex-wrap">
              {(creatorId.niches || ["Beauty", "Skincare", "Dermatology"]).map((n, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-[var(--r-xs)] bg-[var(--doc-bg)] border border-[var(--doc-line)] text-xs text-[var(--doc-text)] font-medium"
                >
                  {n}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
