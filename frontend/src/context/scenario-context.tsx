import { createContext, useContext, useState, type ReactNode } from "react";

type ScenarioContextValue = {
  scenarioId: string;
  setScenarioId: (id: string) => void;
  timeframe: "full" | "recent";
  setTimeframe: (range: "full" | "recent") => void;
};

const ScenarioContext = createContext<ScenarioContextValue | undefined>(
  undefined,
);

export function ScenarioProvider({ children }: { children: ReactNode }) {
  const [scenarioId, setScenarioId] = useState("costAware");
  const [timeframe, setTimeframe] = useState<"full" | "recent">("full");

  return (
    <ScenarioContext.Provider
      value={{ scenarioId, setScenarioId, timeframe, setTimeframe }}
    >
      {children}
    </ScenarioContext.Provider>
  );
}

export function useScenario() {
  const ctx = useContext(ScenarioContext);
  if (!ctx) {
    throw new Error("useScenario must be used within ScenarioProvider");
  }
  return ctx;
}
