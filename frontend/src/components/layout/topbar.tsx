import { useQuery } from "@tanstack/react-query";
import { Rocket } from "lucide-react";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { useScenario } from "@/context/scenario-context";
import { fetchScenarios } from "@/lib/api";

export function Topbar() {
  const { scenarioId, setScenarioId } = useScenario();
  const { data: scenarioOptions = [] } = useQuery({
    queryKey: ["scenarios"],
    queryFn: fetchScenarios,
  });

  return (
    <header className="sticky top-0 z-20 flex items-center gap-4 border-b border-border/70 bg-gradient-to-r from-background/90 via-background/80 to-background/70 px-6 py-4 backdrop-blur-xl">
      <div className="flex flex-1 flex-col gap-2 md:flex-row md:items-center md:gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/15 text-primary shadow-inner">
            <Rocket className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              Scenario
            </p>
            <div className="flex items-center gap-2">
              <Select
                value={scenarioId}
                onValueChange={(value) => setScenarioId(value)}
              >
                <SelectTrigger className="w-[460px] border-border/70 bg-card text-sm">
                  <SelectValue placeholder="Select scenario" />
                </SelectTrigger>
                <SelectContent className="bg-card text-foreground shadow-lg border border-border/70">
                  {scenarioOptions.map((scenario) => (
                    <SelectItem value={scenario.id} key={scenario.id}>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium whitespace-nowrap">
                          {scenario.name}
                        </span>
                        <span className="text-[11px] text-muted-foreground whitespace-nowrap">
                          · {scenario.description}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 md:justify-end">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
