import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "@/lib/auth";

// Portals & Pages
import { LoginPage } from "./pages/Login";
import { CompanyDashboard } from "./portals/company/Dashboard";
import { CampaignsList } from "./portals/company/CampaignsList";
import { CampaignDetail } from "./portals/company/CampaignDetail";
import { NewCampaign } from "./portals/company/NewCampaign";
import { ContractReview } from "./portals/company/ContractReview";
import { ContractDiff } from "./portals/company/ContractDiff";
import { SubmissionReview } from "./portals/company/SubmissionReview";
import { ReportsArchive } from "./portals/company/ReportsArchive";
import { CompanySettings } from "./portals/company/Settings";

import { CreatorHome } from "./portals/creator/Home";
import { PreflightCheck } from "./portals/creator/Preflight";
import { SubmitFinal } from "./portals/creator/SubmitFinal";
import { CreatorSubmissionStatus } from "./portals/creator/SubmissionStatus";
import { CreatorIDCredential } from "./portals/creator/CreatorID";
import { PublicCreatorID } from "./portals/creator/PublicCreatorID";

import { AdjudicationQueue } from "./portals/admin/AdjudicationQueue";
import { PipelineHealth } from "./portals/admin/PipelineHealth";
import { AdminMetricsView } from "./portals/admin/Metrics";
import { AuditLogView } from "./portals/admin/AuditLog";

function RoleRedirect() {
  const { user, isLoading } = useAuth();
  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;

  if (user.role === "creator") return <Navigate to="/creator" replace />;
  if (user.role === "platform_admin") return <Navigate to="/admin" replace />;
  return <Navigate to="/company" replace />;
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RoleRedirect />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Public Unauthenticated CreatorID Route */}
        <Route path="/c/:handle" element={<PublicCreatorID />} />

        {/* Company Portal */}
        <Route path="/company" element={<CompanyDashboard />} />
        <Route path="/company/campaigns" element={<CampaignsList />} />
        <Route path="/company/campaigns/new" element={<NewCampaign />} />
        <Route path="/company/campaigns/:id" element={<CampaignDetail />} />
        <Route path="/company/contracts/:id/review" element={<ContractReview />} />
        <Route path="/company/contracts/:id/diff/:otherId" element={<ContractDiff />} />
        <Route path="/company/submissions/:id/review" element={<SubmissionReview />} />
        <Route path="/company/reports" element={<ReportsArchive />} />
        <Route path="/company/settings" element={<CompanySettings />} />

        {/* Creator Portal */}
        <Route path="/creator" element={<CreatorHome />} />
        <Route path="/creator/preflight" element={<PreflightCheck />} />
        <Route path="/creator/submit" element={<SubmitFinal />} />
        <Route path="/creator/submissions/:id" element={<CreatorSubmissionStatus />} />
        <Route path="/creator/creatorid" element={<CreatorIDCredential />} />

        {/* Admin Console */}
        <Route path="/admin" element={<AdjudicationQueue />} />
        <Route path="/admin/jobs" element={<PipelineHealth />} />
        <Route path="/admin/metrics" element={<AdminMetricsView />} />
        <Route path="/admin/audit" element={<AuditLogView />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
