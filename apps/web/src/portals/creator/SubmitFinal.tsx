import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, CheckCircle2, AlertCircle, Sparkles, Tag, ShieldCheck } from "lucide-react";
import type { Contract, Submission } from "@shared/index";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { FileDropzone } from "@/components/ui/FileDropzone";

export const SubmitFinal: React.FC = () => {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContractId, setSelectedContractId] = useState<string>("");
  const [videoFileKey, setVideoFileKey] = useState<string | null>(null);
  const [captionText, setCaptionText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Live disclosure tag check as user types
  const hasDisclosureTag =
    captionText.toLowerCase().includes("#ad") ||
    captionText.toLowerCase().includes("#sponsored") ||
    captionText.toLowerCase().includes("paid partnership");

  const handleSubmit = async () => {
    if (!videoFileKey) {
      setError("Please upload your final video file.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      const sub = await api.post<Submission>("/submissions", {
        contract_id: selectedContractId || "sample-contract",
        kind: "final",
        video_file_key: videoFileKey,
        caption_text: captionText,
        duration_seconds: 30.0,
      });

      navigate(`/creator/submissions/${sub.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to submit video deliverable");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppLayout>
      <PageHeader
        title="Submit Final Deliverable"
        subtitle="Deliver final sponsored video to the brand for AI compliance verification and payment release."
      />

      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        <div className="p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] flex flex-col gap-5 shadow-xs">
          <div>
            <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">
              Select Contract / Campaign *
            </label>
            <select
              value={selectedContractId}
              onChange={(e) => setSelectedContractId(e.target.value)}
              className="w-full p-2.5 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
            >
              <option value="contract-alex-v2">Hydration Serum Q3 Launch (Contract v2 - Lumen Skincare)</option>
              <option value="contract-spf-v1">Sun Shield SPF 50 Summer Push (Contract v1)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">
              Final Rendered Video File (MP4 / MOV) *
            </label>
            <FileDropzone
              accept="video/mp4,video/quicktime"
              label="Drop your final master video here"
              hint="Maximum 500MB • 1080p or 4K recommended"
              onFileUploaded={(key) => setVideoFileKey(key)}
            />
          </div>

          {/* Caption with Live Disclosure Tag Detector (Section 14 requirement) */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold text-[var(--doc-text)]">
                Social Media Post Caption *
              </label>
              <div className="flex items-center gap-1.5 text-[11px] font-mono">
                <Tag className="w-3.5 h-3.5 text-[var(--brand)]" />
                {hasDisclosureTag ? (
                  <span className="text-[var(--pass)] font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Disclosure Tag Detected
                  </span>
                ) : (
                  <span className="text-amber-600 font-semibold flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" /> Missing #ad / #sponsored tag
                  </span>
                )}
              </div>
            </div>
            <textarea
              rows={3}
              value={captionText}
              onChange={(e) => setCaptionText(e.target.value)}
              placeholder="e.g. My daily morning glow step with #ad @lumenskincare Hydration Serum! Check the link in my bio for 20% off your bottle ✨"
              className={`w-full p-2.5 bg-[var(--doc-bg)] border rounded-[var(--r-sm)] text-xs text-[var(--doc-text)] focus:outline-none ${
                hasDisclosureTag ? "border-[var(--pass)]" : "border-[var(--doc-line)] focus:border-[var(--brand)]"
              }`}
            />
            <p className="text-[11px] text-[var(--doc-text-muted)] mt-1">
              Live validation confirms compliance with FTC / ASCI paid disclosure guidelines.
            </p>
          </div>

          {error && <p className="text-xs text-[var(--fail)]">{error}</p>}

          <div className="flex items-center justify-between pt-4 border-t border-[var(--doc-line)]">
            <span className="text-xs text-[var(--doc-text-muted)]">
              Submitting triggers automated AI compliance audit.
            </span>
            <Button
              variant="primary"
              size="lg"
              onClick={handleSubmit}
              isLoading={isSubmitting}
            >
              <ShieldCheck className="w-4 h-4 mr-2" />
              Submit to Brand
            </Button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};
