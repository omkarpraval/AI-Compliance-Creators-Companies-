import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Check, ChevronRight, FileText, Sparkles, Users } from "lucide-react";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/patterns/AppLayout";
import { PageHeader } from "@/components/patterns/PageHeader";
import { Button } from "@/components/ui/Button";
import { FileDropzone } from "@/components/ui/FileDropzone";

export const NewCampaign: React.FC = () => {
  const navigate = useNavigate();

  // Persistent draft state in localStorage so refresh never loses work
  const [step, setStep] = useState(1);
  const [name, setName] = useState(() => localStorage.getItem("draft_camp_name") || "");
  const [productName, setProductName] = useState(() => localStorage.getItem("draft_camp_product") || "");
  const [description, setDescription] = useState(() => localStorage.getItem("draft_camp_desc") || "");
  const [startsOn, setStartsOn] = useState(() => localStorage.getItem("draft_camp_start") || "2026-09-01");
  const [endsOn, setEndsOn] = useState(() => localStorage.getItem("draft_camp_end") || "2026-11-30");
  const [contractFileKey, setContractFileKey] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem("draft_camp_name", name);
    localStorage.setItem("draft_camp_product", productName);
    localStorage.setItem("draft_camp_desc", description);
    localStorage.setItem("draft_camp_start", startsOn);
    localStorage.setItem("draft_camp_end", endsOn);
  }, [name, productName, description, startsOn, endsOn]);

  const handleFinish = async () => {
    if (!name || !productName) {
      setError("Please fill in the campaign and product name.");
      setStep(1);
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      // 1. Create campaign
      const camp = await api.post<any>("/campaigns", {
        name,
        product_name: productName,
        description,
        starts_on: startsOn,
        ends_on: endsOn,
      });

      // Clear draft storage
      localStorage.removeItem("draft_camp_name");
      localStorage.removeItem("draft_camp_product");
      localStorage.removeItem("draft_camp_desc");

      navigate(`/company/campaigns/${camp.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create campaign");
    } finally {
      setIsSubmitting(false);
    }
  };

  const steps = [
    { num: 1, title: "Campaign Details" },
    { num: 2, title: "Contract & Brief" },
    { num: 3, title: "Invite Creators" },
  ];

  return (
    <AppLayout>
      <PageHeader
        title="Create New Campaign"
        subtitle="Set campaign objectives, upload governing contract templates, and define requirements."
        actions={
          <Button variant="secondary" onClick={() => navigate("/company/campaigns")}>
            Cancel
          </Button>
        }
      />

      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        {/* Visible 3-Step Stepper */}
        <div className="flex items-center justify-between p-4 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)]">
          {steps.map((s, idx) => (
            <React.Fragment key={s.num}>
              <div className="flex items-center gap-2">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    step > s.num
                      ? "bg-[var(--pass)] text-white"
                      : step === s.num
                      ? "bg-[var(--brand)] text-white"
                      : "bg-gray-100 text-gray-500"
                  }`}
                >
                  {step > s.num ? <Check className="w-3.5 h-3.5" /> : s.num}
                </div>
                <span
                  className={`text-xs font-medium ${
                    step === s.num ? "text-[var(--doc-text)] font-semibold" : "text-[var(--doc-text-muted)]"
                  }`}
                >
                  {s.title}
                </span>
              </div>
              {idx < steps.length - 1 && <ChevronRight className="w-4 h-4 text-[var(--doc-text-faint)]" />}
            </React.Fragment>
          ))}
        </div>

        {/* Step 1: Details */}
        {step === 1 && (
          <div className="p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] flex flex-col gap-4">
            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">Campaign Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Q4 Hydration Serum Launch"
                className="w-full p-2.5 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)] focus:outline-none focus:border-[var(--brand)]"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">Featured Product *</label>
              <input
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                placeholder="e.g. Lumen Hydration Serum"
                className="w-full p-2.5 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)] focus:outline-none focus:border-[var(--brand)]"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">Start Date</label>
                <input
                  type="date"
                  value={startsOn}
                  onChange={(e) => setStartsOn(e.target.value)}
                  className="w-full p-2 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">End Date</label>
                <input
                  type="date"
                  value={endsOn}
                  onChange={(e) => setEndsOn(e.target.value)}
                  className="w-full p-2 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">Campaign Description</label>
              <textarea
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Key deliverables, creator guidelines, and primary goals..."
                className="w-full p-2.5 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)]"
              />
            </div>

            <div className="flex justify-end pt-3">
              <Button variant="primary" onClick={() => setStep(2)}>
                Next: Contract & Brief →
              </Button>
            </div>
          </div>
        )}

        {/* Step 2: Upload Contract Brief */}
        {step === 2 && (
          <div className="p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] flex flex-col gap-4">
            <div>
              <h3 className="text-sm font-semibold text-[var(--doc-text)]">Upload Influencer Agreement PDF</h3>
              <p className="text-xs text-[var(--doc-text-muted)] mt-0.5">
                Verifyd will extract all obligations into a machine-checkable compliance checklist.
              </p>
            </div>

            <FileDropzone
              accept="application/pdf"
              label="Drop your contract PDF here"
              hint="Extracts clauses for logo timing, spoken seconds, competitor restrictions..."
              onFileUploaded={(key) => setContractFileKey(key)}
            />

            <div className="flex justify-between pt-3">
              <Button variant="secondary" onClick={() => setStep(1)}>
                ← Back
              </Button>
              <Button variant="primary" onClick={() => setStep(3)}>
                Next: Creators →
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Creator Selection & Confirmation */}
        {step === 3 && (
          <div className="p-6 bg-[var(--doc-surface)] rounded-[var(--r-md)] border border-[var(--doc-line)] flex flex-col gap-4">
            <div>
              <h3 className="text-sm font-semibold text-[var(--doc-text)]">Invite Creators & Launch</h3>
              <p className="text-xs text-[var(--doc-text-muted)] mt-0.5">
                Review setup before creating campaign workspace.
              </p>
            </div>

            <div className="p-4 bg-[var(--doc-bg)] rounded-[var(--r-sm)] border border-[var(--doc-line)] flex flex-col gap-2 text-xs">
              <div className="flex justify-between">
                <span className="text-[var(--doc-text-muted)]">Campaign:</span>
                <span className="font-semibold text-[var(--doc-text)]">{name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--doc-text-muted)]">Product:</span>
                <span className="font-semibold text-[var(--doc-text)]">{productName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--doc-text-muted)]">Timeline:</span>
                <span className="font-mono text-[var(--doc-text)]">
                  {startsOn} to {endsOn}
                </span>
              </div>
            </div>

            {error && <p className="text-xs text-[var(--fail)]">{error}</p>}

            <div className="flex justify-between pt-3">
              <Button variant="secondary" onClick={() => setStep(2)}>
                ← Back
              </Button>
              <Button variant="primary" onClick={handleFinish} isLoading={isSubmitting}>
                Launch Campaign
              </Button>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
};
