import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Leaf,
  Network,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useScenario } from "@/context/scenario-context";
import { fetchDashboard } from "@/lib/api";
import { formatCost, formatNumber } from "@/lib/utils";
import type {
  DashboardPayload,
  NetworkEdge,
  NetworkNode,
  PenaltySlice,
} from "@/lib/types";

function KPIBlock({ kpi }: { kpi: DashboardPayload["kpis"][number] }) {
  const isPositive = (kpi.delta ?? 0) >= 0;
  return (
    <Card className="glass h-full">
      <CardContent className="flex flex-col gap-4 p-4">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{kpi.label}</span>
          {typeof kpi.delta === "number" ? (
            <span
              className={`flex items-center gap-1 text-xs font-semibold ${
                isPositive ? "text-emerald-500" : "text-rose-500"
              }`}
            >
              {isPositive ? (
                <ArrowUpRight className="h-3.5 w-3.5" />
              ) : (
                <ArrowDownRight className="h-3.5 w-3.5" />
              )}
              {kpi.delta.toFixed(1)}%
            </span>
          ) : null}
        </div>
        <p className="text-2xl font-semibold">
          {kpi.unit === "cost" ? formatCost(kpi.value) : formatNumber(kpi.value)}
        </p>
        {kpi.helper ? (
          <p className="text-xs text-muted-foreground">{kpi.helper}</p>
        ) : null}
      </CardContent>
    </Card>
  );
}

function CostPenaltyChart({ data }: { data: DashboardPayload }) {
  return (
    <Card className="glass">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>Cost & Penalty over Time</CardTitle>
          <p className="text-sm text-muted-foreground">
            Operational vs penalties per round
          </p>
        </div>
        <Badge variant="muted">Live</Badge>
      </CardHeader>
      <CardContent className="h-[280px] w-full">
        <ResponsiveContainer>
          <AreaChart data={data.costSeries}>
            <defs>
              <linearGradient id="op" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="pen" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#f97316" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#f97316" stopOpacity={0.08} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="4 4" stroke="hsl(var(--border))" />
            <XAxis dataKey="round" tickLine={false} axisLine={false} />
            <YAxis tickLine={false} axisLine={false} />
            <Tooltip
              content={({ payload }) => {
                if (!payload?.length) return null;
                const point = payload[0].payload as (typeof data.costSeries)[number];
                return (
                  <div className="rounded-lg border bg-card/90 p-3 shadow-lg">
                    <p className="text-sm font-semibold">Round {point.round}</p>
                    <p className="text-xs text-foreground">
                      Operational: {formatCost(point.operational * 1000)}
                    </p>
                    <p className="text-xs text-foreground">
                      Penalties: {formatCost(point.penalty * 1000)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Total: {formatCost(point.total * 1000)}
                    </p>
                  </div>
                );
              }}
            />
            <Area
              type="monotone"
              dataKey="operational"
              stroke="#0ea5e9"
              fill="url(#op)"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="penalty"
              stroke="#f97316"
              fill="url(#pen)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function PenaltyBreakdown({ data }: { data: PenaltySlice[] }) {
  const total = data.reduce((acc, slice) => acc + slice.value, 0);
  const topPain = data[0];

  return (
    <Card className="glass">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>Penalty Breakdown</CardTitle>
          <p className="text-sm text-muted-foreground">Where the pain comes from</p>
        </div>
        <Badge variant="warning">{Math.round(total)} pts</Badge>
      </CardHeader>
      <CardContent className="flex gap-6">
        <div className="h-[220px] w-1/2">
          <ResponsiveContainer>
            <PieChart>
              <Tooltip
                formatter={(value: number, name: string) => [
                  `${value.toFixed(0)} pts`,
                  name,
                ]}
              />
              <Pie
                data={data}
                dataKey="value"
                nameKey="type"
                innerRadius={60}
                outerRadius={90}
                stroke="hsl(var(--background))"
                strokeWidth={4}
              >
                {data.map((entry, index) => (
                  <Cell
                    key={entry.type}
                    fill={
                      entry.color ??
                      [
                        "#0ea5e9",
                        "#22c55e",
                        "#f97316",
                        "#a855f7",
                        "#f43f5e",
                        "#eab308",
                      ][index % 6]
                    }
                  />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-1 flex-col justify-between">
          <div className="space-y-2">
            {data.map((slice) => (
              <div key={slice.type} className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">{slice.type}</span>
                <span className="text-sm font-semibold text-foreground">
                  {slice.value.toFixed(0)} pts
                </span>
              </div>
            ))}
          </div>
          <div className="rounded-xl bg-secondary p-3 text-sm text-secondary-foreground shadow-inner">
            <p className="font-semibold">
              {topPain
                ? `${topPain.type} is the largest contributor.`
                : "Penalties are balanced across categories."}
            </p>
            <p className="text-muted-foreground">
              {topPain
                ? "Focus on demand smoothing and better buffers on long-haul Economy to curb it."
                : "Great position; keep monitoring long-haul economy and hub reserves."}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function NetworkSnapshot({
  nodes,
  edges,
}: {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}) {
  return (
    <Card className="glass">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>Network Snapshot</CardTitle>
          <p className="text-sm text-muted-foreground">Buffers & flows</p>
        </div>
        <Badge variant="muted">6 airports</Badge>
      </CardHeader>
      <CardContent>
        <div className="relative h-[260px] overflow-hidden rounded-xl border border-border/60 bg-gradient-to-br from-card via-card to-primary/5">
          <svg viewBox="0 0 100 60" className="absolute inset-0 h-full w-full">
            {edges.map((edge) => {
              const from = nodes.find((n) => n.code === edge.from);
              const to = nodes.find((n) => n.code === edge.to);
              if (!from || !to) return null;
              return (
                <line
                  key={`${edge.from}-${edge.to}`}
                  x1={from.x * 100}
                  y1={from.y * 60}
                  x2={to.x * 100}
                  y2={to.y * 60}
                  stroke="url(#flow)"
                  strokeWidth={Math.max(1.5, edge.volume / 60)}
                  opacity={0.65}
                  strokeLinecap="round"
                />
              );
            })}
            <defs>
              <linearGradient id="flow" x1="0" x2="1" y1="0" y2="0">
                <stop offset="0%" stopColor="#0ea5e9" stopOpacity={0.7} />
                <stop offset="100%" stopColor="#22c55e" stopOpacity={0.7} />
              </linearGradient>
            </defs>
            {nodes.map((node) => {
              const ratio = node.stock / node.capacity;
              const color =
                ratio > 0.9
                  ? "#f97316"
                  : ratio < 0.35
                    ? "#ef4444"
                    : "#0ea5e9";
              return (
                <g key={node.code} transform={`translate(${node.x * 100}, ${node.y * 60})`}>
                  <circle
                    r={6}
                    fill={color}
                    opacity={0.85}
                    stroke="white"
                    strokeWidth={1}
                  />
                  <text
                    x={0}
                    y={-10}
                    textAnchor="middle"
                    className="text-[6px] font-semibold fill-foreground"
                  >
                    {node.code}
                  </text>
                </g>
              );
            })}
          </svg>
          <div className="absolute right-3 top-3 flex items-center gap-2 rounded-full bg-background/80 px-3 py-1 text-xs text-muted-foreground shadow-inner">
            <Network className="h-4 w-4 text-primary" />
            Live average flow per round
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function StrategySummary({ data }: { data: DashboardPayload }) {
  return (
    <Card className="glass">
      <CardHeader className="flex flex-row items-start justify-between pb-2">
        <div>
          <CardTitle>{data.strategy.title}</CardTitle>
          <p className="text-sm text-muted-foreground">{data.strategy.description}</p>
        </div>
        <Badge variant="success" className="gap-1">
          <Leaf className="h-4 w-4" />
          Tuned
        </Badge>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {data.strategy.chips.map((chip) => (
            <Badge key={chip} variant="muted">
              {chip}
            </Badge>
          ))}
        </div>
        <ul className="space-y-2 text-sm text-muted-foreground">
          {data.strategy.rules.map((rule) => (
            <li key={rule} className="flex gap-2">
              <span className="mt-1 h-2 w-2 rounded-full bg-primary/60" />
              <span>{rule}</span>
            </li>
          ))}
        </ul>
        <div className="rounded-xl bg-primary/10 p-3 text-sm">
          <p className="font-semibold text-primary">Insight</p>
          <p className="text-primary/90">{data.highlight}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function DashboardContent({ data }: { data: DashboardPayload }) {
  return (
    <div className="space-y-4">
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="bg-card">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
          <TabsTrigger value="strategy">Strategy</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-3 md:grid-cols-4">
            {data.kpis.map((kpi) => (
              <KPIBlock key={kpi.label} kpi={kpi} />
            ))}
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <CostPenaltyChart data={data} />
            </div>
            <PenaltyBreakdown data={data.penaltyBreakdown} />
          </div>
        </TabsContent>
        <TabsContent value="network" className="space-y-4">
          <NetworkSnapshot nodes={data.network.nodes} edges={data.network.edges} />
        </TabsContent>
        <TabsContent value="strategy" className="space-y-4">
          <StrategySummary data={data} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, idx) => (
          <Skeleton key={idx} className="h-28 rounded-2xl" />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Skeleton className="h-[320px] rounded-2xl lg:col-span-2" />
        <Skeleton className="h-[320px] rounded-2xl" />
      </div>
    </div>
  );
}

function DashboardPage() {
  const { scenarioId } = useScenario();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard", scenarioId],
    queryFn: () => fetchDashboard(scenarioId),
  });

  if (isError) {
    return (
      <Card className="glass">
        <CardContent className="flex items-center gap-3 p-6 text-rose-500">
          <AlertTriangle className="h-5 w-5" />
          <div>
            <p className="font-semibold">Unable to load dashboard</p>
            <p className="text-sm text-muted-foreground">
              Check your connection or try selecting a different scenario.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || isLoading) {
    return <LoadingState />;
  }

  return <DashboardContent data={data} />;
}

export default DashboardPage;
