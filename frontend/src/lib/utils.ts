import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCost(value: number) {
  return Intl.NumberFormat("en-US", {
    maximumFractionDigits: value >= 1 ? 0 : 1,
  }).format(value);
}

export function formatNumber(value: number) {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(1)}k`;
  }
  return value.toFixed(0);
}

export function statusColor(status: "ok" | "warning" | "critical") {
  if (status === "ok") return "text-emerald-500 bg-emerald-500/10";
  if (status === "warning") return "text-amber-500 bg-amber-500/10";
  return "text-rose-500 bg-rose-500/10";
}
