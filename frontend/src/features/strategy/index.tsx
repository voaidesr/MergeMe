import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
} from "recharts";
import { Brain, RefreshCw, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchStrategyParams, runSimulation } from "@/lib/api";
import type { SimulationResult, StrategyParams } from "@/lib/types";
import { formatCost, formatNumber } from "@/lib/utils";

type ResultPair = { baseline: SimulationResult; current: SimulationResult };

function ParameterCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-2xl border border-border/70 bg-card p-4 shadow-inner">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">{title}</h3>
      </div>
      <div className="mt-3 space-y-3">{children}</div>
    </div>
  );
}

function ComparisonCard({
  label,
  baseline,
  current,
}: {
  label: string;
  baseline: number;
  current: number;
}) {
  const delta = ((current - baseline) / baseline) * 100;
  const isPositive = delta <= 0;
  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-muted-foreground">{label}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-3">
          <p className="text-2xl font-semibold">{formatCost(current)}</p>
          <p className="text-sm text-muted-foreground">
            vs {formatCost(baseline)}
          </p>
          <Badge variant={isPositive ? "success" : "danger"}>
            {isPositive ? "↓" : "↑"} {Math.abs(delta).toFixed(1)}%
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

function DeltaChart({ result }: { result: ResultPair }) {
  const deltas = useMemo(() => {
    const base = result.baseline.penaltyBreakdown;
    const current = result.current.penaltyBreakdown;
    return base.map((slice) => {
      const currentValue =
        current.find((c) => c.type === slice.type)?.value ?? slice.value;
      return {
        type: slice.type,
        delta: slice.value - currentValue,
      };
    });
  }, [result]);

  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <CardTitle>Penalty deltas</CardTitle>
        <p className="text-sm text-muted-foreground">
          Positive numbers mean an improvement vs baseline
        </p>
      </CardHeader>
      <CardContent className="h-[260px]">
        <ResponsiveContainer>
          <BarChart data={deltas}>
            <CartesianGrid strokeDasharray="4 4" stroke="hsl(var(--border))" />
            <XAxis dataKey="type" tickLine={false} axisLine={false} />
            <Tooltip
              formatter={(value: number) => [`${value.toFixed(0)} pts`, "Delta"]}
            />
            <Bar dataKey="delta" fill="#0ea5e9" radius={8} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function Insights({ result }: { result: ResultPair }) {
  return (
    <Card className="glass">
      <CardHeader className="flex items-center justify-between pb-2">
        <div>
          <CardTitle>Policy behavior</CardTitle>
          <p className="text-sm text-muted-foreground">
            Quick takeaways from the tuned run
          </p>
        </div>
        <Badge variant="muted">Explainable</Badge>
      </CardHeader>
      <CardContent className="space-y-2 text-sm text-muted-foreground">
        <div className="flex gap-2">
          <span className="mt-1 h-2 w-2 rounded-full bg-primary" />
          <span>
            Premium cabins maintained while total penalties dropped to{" "}
            {formatNumber(result.current.penalties)}.
          </span>
        </div>
        <div className="flex gap-2">
          <span className="mt-1 h-2 w-2 rounded-full bg-primary" />
          <span>
            Long-haul economy throttled; expect leaner buffers at outstations, check NRT/JFK.
          </span>
        </div>
        <div className="flex gap-2">
          <span className="mt-1 h-2 w-2 rounded-full bg-primary" />
          <span>
            Operational spend within tolerance; consider one more episode to stabilize.
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

function StrategyLabPage() {
  const { data: defaults, isLoading } = useQuery({
    queryKey: ["strategy-params"],
    queryFn: fetchStrategyParams,
  });
  const [params, setParams] = useState<StrategyParams | null>(null);

  useEffect(() => {
    if (defaults) {
      setParams(defaults);
    }
  }, [defaults]);

  const simulation = useMutation({
    mutationFn: runSimulation,
  });

  const resultPair: ResultPair | null = simulation.data ?? null;

  const handleBiasChange = (cabin: string, value: number[]) => {
    if (!params) return;
    setParams({ ...params, biases: { ...params.biases, [cabin]: value[0] } });
  };

  const handleAlphaChange = (cabin: string, value: number[]) => {
    if (!params) return;
    setParams({ ...params, costAlpha: { ...params.costAlpha, [cabin]: value[0] } });
  };

  if (isLoading || !params) {
    return <Skeleton className="h-[520px] rounded-2xl" />;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Brain className="h-5 w-5 text-primary" />
        <h1 className="text-2xl font-semibold">Strategy Lab</h1>
        <Badge variant="muted">Heuristic + RL</Badge>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-3">
          <ParameterCard title="Class priorities (BIAS)">
            {Object.entries(params.biases).map(([cabin, value]) => (
              <div key={cabin}>
                <div className="flex items-center justify-between text-sm">
                  <span>{cabin}</span>
                  <span className="text-muted-foreground">{value.toFixed(2)}</span>
                </div>
                <Slider
                  value={[value]}
                  min={0.6}
                  max={1.6}
                  step={0.05}
                  onValueChange={(v) => handleBiasChange(cabin, v)}
                />
              </div>
            ))}
          </ParameterCard>

          <ParameterCard title="Distance thresholds (km)">
            {Object.entries(params.distanceThresholds).map(([label, value]) => (
              <div key={label} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="capitalize">{label}</span>
                  <span className="text-muted-foreground">{value}</span>
                </div>
                <Slider
                  value={[value]}
                  min={600}
                  max={9000}
                  step={200}
                  onValueChange={(v) =>
                    setParams({
                      ...params,
                      distanceThresholds: { ...params.distanceThresholds, [label]: v[0] },
                    })
                  }
                />
              </div>
            ))}
          </ParameterCard>

          <ParameterCard title="Cost vs penalty α">
            {Object.entries(params.costAlpha).map(([cabin, value]) => (
              <div key={cabin}>
                <div className="flex items-center justify-between text-sm">
                  <span>{cabin}</span>
                  <span className="text-muted-foreground">{value.toFixed(2)}</span>
                </div>
                <Slider
                  value={[value]}
                  min={0.5}
                  max={1.5}
                  step={0.05}
                  onValueChange={(v) => handleAlphaChange(cabin, v)}
                />
              </div>
            ))}
          </ParameterCard>

          <ParameterCard title="Long-haul toggles">
            {Object.entries(params.holdOnLong).map(([cabin, value]) => (
              <div key={cabin} className="flex items-center justify-between text-sm">
                <span>Hold {cabin} on long flights</span>
                <Switch
                  checked={value}
                  onCheckedChange={(checked) =>
                    setParams({
                      ...params,
                      holdOnLong: { ...params.holdOnLong, [cabin]: checked },
                    })
                  }
                />
              </div>
            ))}
          </ParameterCard>

          <ParameterCard title="Run settings">
            <div className="flex items-center gap-3">
              <div className="space-y-1">
                <Label>Episodes</Label>
                <Input
                  type="number"
                  value={params.episodes}
                  onChange={(e) =>
                    setParams({ ...params, episodes: Number(e.target.value) })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label>Seed</Label>
                <Input
                  type="number"
                  value={params.seed}
                  onChange={(e) =>
                    setParams({ ...params, seed: Number(e.target.value) })
                  }
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                className="flex-1"
                onClick={() => params && simulation.mutate(params)}
                disabled={simulation.isPending}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {simulation.isPending ? "Running..." : "Run Simulation"}
              </Button>
              <Button
                variant="ghost"
                onClick={() => defaults && setParams(defaults)}
                disabled={simulation.isPending}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Reset
              </Button>
            </div>
          </ParameterCard>
        </div>

        <div className="lg:col-span-2 space-y-3">
          <Tabs defaultValue="results">
            <TabsList className="bg-card">
              <TabsTrigger value="results">Results</TabsTrigger>
              <TabsTrigger value="behavior">Behavior</TabsTrigger>
            </TabsList>
            <TabsContent value="results" className="space-y-3">
              {resultPair ? (
                <>
                  <div className="grid gap-3 md:grid-cols-3">
                    <ComparisonCard
                      label="Total cost"
                      baseline={resultPair.baseline.totalCost}
                      current={resultPair.current.totalCost}
                    />
                    <ComparisonCard
                      label="Operational cost"
                      baseline={resultPair.baseline.operational}
                      current={resultPair.current.operational}
                    />
                    <ComparisonCard
                      label="Penalties"
                      baseline={resultPair.baseline.penalties}
                      current={resultPair.current.penalties}
                    />
                  </div>
                  <DeltaChart result={resultPair} />
                </>
              ) : (
                <div className="rounded-2xl border border-dashed border-border/70 p-6 text-center text-muted-foreground">
                  Run a simulation to compare against the baseline.
                </div>
              )}
            </TabsContent>
            <TabsContent value="behavior">
              {resultPair ? (
                <Insights result={resultPair} />
              ) : (
                <div className="rounded-2xl border border-dashed border-border/70 p-6 text-center text-muted-foreground">
                  Behavior insights will appear after a run.
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

export default StrategyLabPage;
