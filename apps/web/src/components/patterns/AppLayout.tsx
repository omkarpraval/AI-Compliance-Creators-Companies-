import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Shield,
  Layers,
  FileCheck2,
  Users,
  BarChart3,
  LogOut,
  Sparkles,
  ExternalLink,
  Sliders,
  CheckCircle,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/Button";

export const AppLayout: React.FC<{ children: React.ReactNode; isDarkWorkspace?: boolean }> = ({
  children,
  isDarkWorkspace = false,
}) => {
  const { user, logout, switchUserRole } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const navItems = [
    ...(user?.role === "company_admin" || user?.role === "company_member"
      ? [
          { label: "Dashboard", href: "/company", icon: Layers },
          { label: "Campaigns", href: "/company/campaigns", icon: FileCheck2 },
          { label: "Reports Archive", href: "/company/reports", icon: BarChart3 },
          { label: "Settings", href: "/company/settings", icon: Sliders },
        ]
      : []),
    ...(user?.role === "creator"
      ? [
          { label: "Home", href: "/creator", icon: Layers },
          { label: "Pre-Flight", href: "/creator/preflight", icon: Sparkles },
          { label: "Submit Video", href: "/creator/submit", icon: FileCheck2 },
          { label: "CreatorID™", href: "/creator/creatorid", icon: Shield },
        ]
      : []),
    ...(user?.role === "platform_admin"
      ? [
          { label: "Adjudication Queue", href: "/admin", icon: Layers },
          { label: "Pipeline Health", href: "/admin/jobs", icon: BarChart3 },
          { label: "Metrics & Spend", href: "/admin/metrics", icon: Sliders },
          { label: "Audit Log", href: "/admin/audit", icon: FileCheck2 },
        ]
      : []),
  ];

  const headerBg = isDarkWorkspace
    ? "bg-[var(--ev-surface)] border-[var(--ev-line)] text-[var(--ev-text)]"
    : "bg-[var(--doc-surface)] border-[var(--doc-line)] text-[var(--doc-text)]";

  return (
    <div className={`min-h-screen flex flex-col ${isDarkWorkspace ? "bg-[var(--ev-bg)]" : "bg-[var(--doc-bg)]"}`}>
      {/* Top Demo Persona Switcher Banner */}
      <div className="bg-[#18113C] text-white px-4 py-1.5 flex flex-wrap items-center justify-between text-xs border-b border-[#2C1F6D] select-none">
        <div className="flex items-center gap-2">
          <span className="font-mono font-bold text-[var(--brand-hover)] uppercase tracking-wider">
            VERIFYD DEMO SWITCHER:
          </span>
          <span className="text-gray-300">Signed in as: <strong>{user?.full_name}</strong> ({user?.role})</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-gray-400">Quick switch:</span>
          <button
            onClick={() => switchUserRole("admin@lumenskincare.com")}
            className="px-2 py-0.5 rounded bg-[#2E206A] hover:bg-[var(--brand)] text-[11px] transition-colors cursor-pointer"
          >
            Brand Admin
          </button>
          <button
            onClick={() => switchUserRole("alex@creators.com")}
            className="px-2 py-0.5 rounded bg-[#2E206A] hover:bg-[var(--brand)] text-[11px] transition-colors cursor-pointer"
          >
            Creator (Alex)
          </button>
          <button
            onClick={() => switchUserRole("ops@verifyd.io")}
            className="px-2 py-0.5 rounded bg-[#2E206A] hover:bg-[var(--brand)] text-[11px] transition-colors cursor-pointer"
          >
            Platform Admin
          </button>
        </div>
      </div>

      {/* Main Application Navigation Header */}
      <header className={`sticky top-0 z-30 px-6 py-3 border-b ${headerBg} transition-colors`}>
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2 font-bold text-lg tracking-tight">
              <div className="w-8 h-8 rounded-[var(--r-sm)] bg-[var(--brand)] flex items-center justify-center text-white shadow-xs">
                <Shield className="w-5 h-5" />
              </div>
              <span>Verifyd</span>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    to={item.href}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--r-sm)] text-xs font-medium transition-all ${
                      isActive
                        ? "bg-[var(--brand)] text-white shadow-xs"
                        : isDarkWorkspace
                        ? "text-[var(--ev-text-muted)] hover:text-white hover:bg-[var(--ev-raised)]"
                        : "text-[var(--doc-text-muted)] hover:text-[var(--doc-text)] hover:bg-[var(--doc-bg)]"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* User Profile & Actions */}
          <div className="flex items-center gap-3">
            {user?.role === "creator" && user?.handle && (
              <Link
                to={`/c/${user.handle}`}
                target="_blank"
                className="hidden sm:inline-flex items-center gap-1 text-xs text-[var(--brand)] hover:underline font-medium"
              >
                <span>Public CreatorID™</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </Link>
            )}

            <div className="flex items-center gap-2 pl-2 border-l border-[var(--doc-line)]">
              <div className="w-8 h-8 rounded-full bg-[var(--brand-subtle-d)] border border-[var(--brand)]/30 flex items-center justify-center text-xs font-bold text-[var(--brand-hover)]">
                {user?.full_name?.charAt(0) || "U"}
              </div>
              <button
                onClick={handleLogout}
                className="p-1.5 rounded-[var(--r-sm)] text-[var(--doc-text-muted)] hover:text-[var(--fail)] hover:bg-[var(--fail-subtle)] cursor-pointer"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Page Content Body */}
      <main className="flex-1 w-full max-w-7xl mx-auto p-6">{children}</main>
    </div>
  );
};
