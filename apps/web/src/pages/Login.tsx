import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Sparkles, ArrowRight, Lock, Mail, Users } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/Button";

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("admin@lumenskincare.com");
  const [password, setPassword] = useState("Verifyd!2026");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError(null);
      const user = await login(email, password);
      if (user.role === "creator") {
        navigate("/creator");
      } else if (user.role === "platform_admin") {
        navigate("/admin");
      } else {
        navigate("/company");
      }
    } catch (err: any) {
      setError(err.message || "Invalid email or password");
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = async (presetEmail: string) => {
    setEmail(presetEmail);
    try {
      setIsLoading(true);
      setError(null);
      const user = await login(presetEmail, "Verifyd!2026");
      if (user.role === "creator") {
        navigate("/creator");
      } else if (user.role === "platform_admin") {
        navigate("/admin");
      } else {
        navigate("/company");
      }
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--doc-bg)] flex flex-col justify-center items-center p-6 selection:bg-[var(--brand-subtle)]">
      <div className="w-full max-w-md flex flex-col gap-6">
        {/* Brand Header */}
        <div className="text-center flex flex-col items-center">
          <div className="w-12 h-12 rounded-[var(--r-md)] bg-[var(--brand)] flex items-center justify-center text-white shadow-md mb-3">
            <Shield className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--doc-text)]">Verifyd</h1>
          <p className="text-xs text-[var(--doc-text-muted)] mt-1">
            The Evidence-Based Influencer Compliance Engine
          </p>
        </div>

        {/* Login Card */}
        <div className="p-8 bg-[var(--doc-surface)] rounded-[var(--r-lg)] border border-[var(--doc-line)] shadow-lg flex flex-col gap-5">
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">Work Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--doc-text-faint)]" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)] focus:outline-none focus:border-[var(--brand)]"
                  placeholder="admin@lumenskincare.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[var(--doc-text)] mb-1">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--doc-text-faint)]" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-[var(--doc-bg)] border border-[var(--doc-line)] rounded-[var(--r-sm)] text-xs text-[var(--doc-text)] focus:outline-none focus:border-[var(--brand)]"
                  required
                />
              </div>
            </div>

            {error && <p className="text-xs text-[var(--fail)]">{error}</p>}

            <Button variant="primary" size="lg" type="submit" isLoading={isLoading} className="w-full mt-2">
              Sign In to Portal
            </Button>
          </form>

          {/* Quick Demo Personas (One-click instant login) */}
          <div className="pt-4 border-t border-[var(--doc-line)] flex flex-col gap-2">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[var(--doc-text-muted)] text-center">
              Quick Demo Personas (Verifyd!2026)
            </span>
            <div className="grid grid-cols-3 gap-2 mt-1">
              <button
                type="button"
                onClick={() => handleQuickLogin("admin@lumenskincare.com")}
                className="p-2 rounded-[var(--r-sm)] border border-[var(--doc-line)] hover:border-[var(--brand)] hover:bg-[var(--brand-subtle)] text-[11px] font-semibold text-[var(--doc-text)] transition-colors cursor-pointer"
              >
                Brand Admin
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin("alex@creators.com")}
                className="p-2 rounded-[var(--r-sm)] border border-[var(--doc-line)] hover:border-[var(--brand)] hover:bg-[var(--brand-subtle)] text-[11px] font-semibold text-[var(--doc-text)] transition-colors cursor-pointer"
              >
                Creator (Alex)
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin("ops@verifyd.io")}
                className="p-2 rounded-[var(--r-sm)] border border-[var(--doc-line)] hover:border-[var(--brand)] hover:bg-[var(--brand-subtle)] text-[11px] font-semibold text-[var(--doc-text)] transition-colors cursor-pointer"
              >
                Platform Admin
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
