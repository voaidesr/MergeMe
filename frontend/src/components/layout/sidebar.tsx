import { Link, NavLink } from "react-router-dom";
import {
  Activity,
  MapPinned,
  PanelsTopLeft,
  Plane,
  SlidersHorizontal,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", to: "/", icon: Activity },
  { label: "Flights", to: "/flights", icon: Plane },
  { label: "Airports", to: "/airports", icon: MapPinned },
  { label: "Strategy Lab", to: "/strategy", icon: SlidersHorizontal },
];

export function Sidebar() {
  return (
    <aside className="hidden w-[380px] shrink-0 border-r border-[--sidebar-border] bg-[--sidebar] text-[--sidebar-foreground] shadow-inner shadow-black/20 lg:flex lg:flex-col">
      <div className="flex items-center gap-3 px-5 pb-4 pt-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/20 text-primary">
          <PanelsTopLeft className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">FROX Control</p>
          <p className="text-xs text-white/60">Flight Rotables Ops</p>
        </div>
      </div>

      <nav className="mt-2 flex flex-1 flex-col gap-1 px-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition hover:bg-white/5 hover:text-white",
                  isActive
                    ? "bg-white/10 text-white shadow-inner shadow-black/10"
                    : "text-white/70",
                )
              }
              end={item.to === "/"}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="m-3 rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-white/80">
        <div className="flex items-center gap-2 text-[11px] uppercase tracking-wide text-white/60">
          <span>RL Agent</span>
          <Badge variant="muted" className="bg-emerald-400/15 text-emerald-200">
            Stable
          </Badge>
          <span className="ml-auto font-semibold lowercase text-white">
            fleet_policy_v1
          </span>
        </div>
        <p className="mt-2 text-[11px] text-white/60">
          Heuristic override active.
        </p>
        <Link
          to="/strategy"
          className="mt-3 inline-flex items-center gap-2 text-xs font-semibold text-primary"
        >
          Tweak policy →
        </Link>
      </div>
    </aside>
  );
}
