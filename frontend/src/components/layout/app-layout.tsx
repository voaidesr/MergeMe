import { Outlet } from "react-router-dom";

import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function AppLayout() {
  return (
    <div className="relative min-h-screen bg-background">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-10%] h-72 w-72 -translate-x-1/2 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute bottom-[-15%] right-0 h-80 w-80 rounded-full bg-emerald-400/10 blur-3xl" />
      </div>
      <div className="relative z-10 flex min-h-screen">
        <Sidebar />
        <div className="flex flex-1 flex-col">
          <Topbar />
          <main className="flex-1 space-y-6 p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
