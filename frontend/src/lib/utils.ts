// frontend/src/lib/utils.ts

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

export function formatHours(hours: number | null): string {
  if (hours === null) return "—";
  if (hours < 1) return `${Math.round(hours * 60)}m`;
  if (hours < 24) return `${hours.toFixed(1)}h`;
  return `${(hours / 24).toFixed(1)}d`;
}

export function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric", month: "short", year: "numeric",
  });
}

export function gradeColor(grade: string | null): string {
  switch (grade) {
    case "Excellent": return "text-emerald-400";
    case "Good":      return "text-blue-400";
    case "Fair":      return "text-amber-400";
    case "Poor":      return "text-red-400";
    default:          return "text-slate-400";
  }
}

export function gradeBg(grade: string | null): string {
  switch (grade) {
    case "Excellent": return "bg-emerald-400/10 text-emerald-400 border-emerald-400/20";
    case "Good":      return "bg-blue-400/10 text-blue-400 border-blue-400/20";
    case "Fair":      return "bg-amber-400/10 text-amber-400 border-amber-400/20";
    case "Poor":      return "bg-red-400/10 text-red-400 border-red-400/20";
    default:          return "bg-slate-400/10 text-slate-400 border-slate-400/20";
  }
}

export function directionColor(dir: string): string {
  if (dir === "increasing") return "text-emerald-400";
  if (dir === "declining")  return "text-red-400";
  return "text-slate-400";
}