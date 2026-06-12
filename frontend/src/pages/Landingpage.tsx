// frontend/src/pages/LandingPage.tsx

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BarChart3, GitBranch, Users, HeartPulse, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) navigate("/dashboard");
  }, [isAuthenticated]);

  const handleLogin = async () => {
    console.log("1. Clicked");
    
    try {
      console.log("Before fetch");

      const response = await fetch("/api/v1/auth/login");

      console.log("After fetch");

      console.log("2. Status:", response.status);

      const data = await response.json();

      console.log("3. Response:", data);

      if (data.url) {
        console.log("4. Redirecting to:", data.url);
        window.location.href = data.url;
      } else {
        console.log("No URL returned");
      }
    } catch (err) {
      console.error("Login error:", err);
    }
  };

  return (
    <div className="min-h-screen bg-surface-DEFAULT text-white flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-white/8">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-brand-600 flex items-center justify-center">
            <BarChart3 className="h-4 w-4 text-white" />
          </div>
          <span className="font-semibold tracking-tight">GitAnalytics</span>
        </div>
        <button
          onClick={() => {
            console.log("CLICKED");
          }}
        >
          Login
        </button>
      </nav>

      {/* Hero */}
      <div className="flex flex-1 flex-col items-center justify-center text-center px-6 py-24 animate-fade-in">
        <div className="mb-4 inline-flex items-center rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-1.5 text-xs font-medium text-brand-400">
          Production-grade GitHub analytics
        </div>
        <h1 className="max-w-3xl text-5xl font-bold tracking-tight text-white">
          Deep insights into your{" "}
          <span className="bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent">
            GitHub repositories
          </span>
        </h1>
        <p className="mt-6 max-w-xl text-lg text-slate-400">
          Analyse commits, pull requests, issues, and contributor activity.
          Track health scores, spot trends, and export reports — all for free.
        </p>
        <div className="mt-10 flex gap-4">
          <Button onClick={handleLogin} size="lg">
            Get started free <ArrowRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Feature grid */}
        <div className="mt-20 grid grid-cols-2 gap-4 md:grid-cols-4 max-w-3xl w-full">
          {[
            { icon: GitBranch, label: "Repository Analytics" },
            { icon: Users,     label: "Contributor Insights" },
            { icon: HeartPulse, label: "Health Scores" },
            { icon: BarChart3, label: "Trend Detection" },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex flex-col items-center gap-3 rounded-xl border border-white/8 bg-surface-50 p-5">
              <Icon className="h-6 w-6 text-brand-400" />
              <span className="text-sm font-medium text-slate-300">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}