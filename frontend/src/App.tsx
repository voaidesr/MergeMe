import { Suspense } from "react";
import {
  RouterProvider,
  createBrowserRouter,
  Navigate,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ThemeProvider } from "@/components/theme/theme-provider";
import { AppLayout } from "@/components/layout/app-layout";
import DashboardPage from "@/features/dashboard";
import FlightsPage from "@/features/flights";
import AirportsPage from "@/features/airports";
import StrategyLabPage from "@/features/strategy";
import { ScenarioProvider } from "@/context/scenario-context";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "flights", element: <FlightsPage /> },
      { path: "airports", element: <AirportsPage /> },
      { path: "strategy", element: <StrategyLabPage /> },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);

const queryClient = new QueryClient();

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="frox-theme">
      <QueryClientProvider client={queryClient}>
        <ScenarioProvider>
          <Suspense fallback={<div className="p-6 text-muted-foreground">Loading...</div>}>
            <RouterProvider router={router} />
          </Suspense>
        </ScenarioProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
