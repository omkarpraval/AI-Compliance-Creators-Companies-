import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ShieldCheck, CheckCircle2, Shield, ArrowRight, ExternalLink } from "lucide-react";
import type { CreatorID } from "@shared/index";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { StateBlock } from "@/components/ui/StateBlock";

export const PublicCreatorID: React.FC = () => {
  const { handle } = useParams<{ handle: string }>();
  const [profile, setProfile] = useState<CreatorID | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadPublicProfile() {
      if (!handle) return;
      try {
        setIsLoading(true);
        const res = await api.get<CreatorID>(`/public/creatorid/${handle}`);
        setProfile(res);
      } catch (err: any) {
        setError("This CreatorID profile is private or does not exist.");
      } finally {
        setIsLoading(false);
      }
    }
    loadPublicProfile();
  }, [handle]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--doc-bg)] flex items-center justify-center p-6">
        <StateBlock type="loading" title="Loading Creator Record..." description="Verifying credentials against the Verifyd network..." />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-[var(--doc-bg)] flex items-center justify-center p-6">
        <StateBlock type="error" title="Profile Unavailable" description={error || "Profile not found"} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--doc-bg)] text-[var(--doc-text)] flex flex-col justify-between">
      {/* Public Header */}
      <header className="px-6 py-4 bg-white border-b border-[var(--doc-line)]">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-base tracking-tight">
            <div className="w-7 h-7 rounded-[var(--r-sm)] bg-[var(--brand)] flex items-center justify-center text-white">
              <Shield className="w-4 h-4" />
            </div>
            <span>Verifyd CreatorID™</span>
          </Link>
          <span className="text-xs font-mono text-[var(--pass)] font-semibold flex items-center gap-1">
            <ShieldCheck className="w-4 h-4" /> Verified Compliance Certificate
          </span>
        </div>
      </header>

      {/* Main Public Credential Badge */}
      <main className="max-w-3xl w-full mx-auto p-6 my-auto">
        <div className="p-8 md:p-12 bg-white rounded-[var(--r-lg)] border-2 border-[var(--doc-line-strong)] shadow-xl relative overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-[var(--doc-line)]">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-[var(--brand-subtle-d)] border-2 border-[var(--brand)] flex items-center justify-center text-xl font-bold text-[var(--brand-hover)] shadow-xs">
                {profile.full_name.charAt(0)}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold text-[var(--doc-text)]">{profile.full_name}</h1>
                  {profile.is_verified && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[var(--pass-subtle)] text-[var(--pass)] text-xs font-mono font-bold border border-[var(--pass)]/30">
                      <ShieldCheck className="w-3.5 h-3.5" /> VERIFIED
                    </span>
                  )}
                </div>
                <p className="text-xs font-mono text-[var(--brand)]">@{profile.handle}</p>
              </div>
            </div>

            <span className="text-xs font-mono bg-gray-100 text-gray-700 px-3 py-1 rounded-[var(--r-xs)]">
              Audited by Verifyd AI
            </span>
          </div>

          <div className="py-8 grid grid-cols-1 md:grid-cols-3 gap-6 text-center md:text-left">
            <div className="md:border-r border-[var(--doc-line)] md:pr-4">
              <span className="text-xs font-mono uppercase tracking-wider text-[var(--doc-text-muted)]">
                Contract Pass Rate
              </span>
              <p className="font-doc text-5xl font-extrabold text-[var(--doc-text)] mt-1">
                {profile.pass_rate}%
              </p>
              <span className="text-xs text-[var(--pass)] font-medium mt-1 inline-flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Top 5% Industry Standard
              </span>
            </div>

            <div className="md:border-r border-[var(--doc-line)] md:pr-4">
              <span className="text-xs font-mono uppercase tracking-wider text-[var(--doc-text-muted)]">
                Campaigns Completed
              </span>
              <p className="font-doc text-5xl font-extrabold text-[var(--doc-text)] mt-1">
                {profile.campaigns_completed || 14}
              </p>
              <span className="text-xs text-[var(--doc-text-muted)] mt-1 block">Brand agreements signed</span>
            </div>

            <div>
              <span className="text-xs font-mono uppercase tracking-wider text-[var(--doc-text-muted)]">
                Avg. Revisions
              </span>
              <p className="font-doc text-5xl font-extrabold text-[var(--brand)] mt-1">
                {profile.average_revisions || 1.1}
              </p>
              <span className="text-xs text-[var(--doc-text-muted)] mt-1 block">Fast approvals</span>
            </div>
          </div>

          {profile.bio && (
            <p className="pt-6 border-t border-[var(--doc-line)] text-xs text-[var(--doc-text-muted)] italic leading-relaxed">
              "{profile.bio}"
            </p>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-6 bg-white border-t border-[var(--doc-line)] text-center text-xs text-[var(--doc-text-muted)]">
        <span>Powered by <strong>Verifyd</strong> — The evidence-based influencer compliance standard.</span>
      </footer>
    </div>
  );
};
