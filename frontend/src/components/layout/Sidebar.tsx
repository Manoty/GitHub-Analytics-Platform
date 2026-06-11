// frontend/src/components/layout/Sidebar.tsx

import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, GitBranch, Users, HeartPulse,
  GitCompare, BarChart3, LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { authApi } from "@/lib/api";

const links = [
  { to: "/dashboard",    label: "Dashboard",    icon: LayoutDashboard },
  { to: "/repositories", label: "Repositories", icon: GitBranch },
  { to: "/contributors", label: "Contributors",  icon: Users },
  { to: "/health",       label: "Health",        icon: HeartPulse },
  { to: "/compare",      label: "Compare",       icon: GitCompare },
];

export function Sidebar() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await authApi.logout().catch(() => {});
    logout();
  };

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-white/8 bg-surface-DEFAULT">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-white/8">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
          <BarChart3 className="h-4 w-4 text-white" />
        </div>
        <span className="font-semibold text-white tracking-tight">GitAnalytics</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-brand-600/20 text-brand-400"
                  : "text-slate-500 hover:bg-white/5 hover:text-slate-300"
              )
            }
          >
            <Icon className="h-4 w-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      {user && (
        <div className="border-t border-white/8 p-3">
          <div className="flex items-center gap-3 rounded-lg px-3 py-2">
            {user.avatar_url && (
              <img src={user.avatar_url} alt={user.username} className="h-7 w-7 rounded-full" />
            )}
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-300">{user.name ?? user.username}</p>
              <p className="truncate text-xs text-slate-600">@{user.username}</p>
            </div>
            <button onClick={handleLogout} className="text-slate-600 hover:text-red-400 transition-colors">
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </aside>
  );
}