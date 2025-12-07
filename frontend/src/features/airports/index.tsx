import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { MapPin, PlaneLanding, PlaneTakeoff } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { fetchAirports, fetchFlights } from "@/lib/api";
import type { Airport } from "@/lib/types";
import { formatNumber } from "@/lib/utils";

function AirportList({
  airports,
  selected,
  onSelect,
}: {
  airports: Airport[];
  selected: string | null;
  onSelect: (code: string) => void;
}) {
  return (
    <Card className="glass">
      <CardHeader className="pb-3">
        <CardTitle>Airports</CardTitle>
        <p className="text-sm text-muted-foreground">
          Buffers & capacity across the network
        </p>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[520px]">
          <div className="divide-y divide-border/70">
            {airports.map((airport) => (
              <button
                key={airport.code}
                onClick={() => onSelect(airport.code)}
                className={`flex w-full items-center justify-between px-4 py-3 text-left transition ${selected === airport.code ? "bg-accent/50" : "hover:bg-accent/30"}`}
              >
                <div>
                  <p className="text-sm font-semibold text-foreground">
                    {airport.code} · {airport.name}
                  </p>
                  <p className="text-xs text-muted-foreground">{airport.type}</p>
                </div>
                <Badge variant={airport.type === "Hub" ? "success" : "muted"}>
                  {airport.type}
                </Badge>
              </button>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

function CapacityCard({
  label,
  stock,
  capacity,
}: {
  label: string;
  stock: number;
  capacity: number;
}) {
  const ratio = stock / capacity;
  const color =
    ratio < 0.35 ? "bg-rose-500" : ratio > 0.9 ? "bg-amber-500" : "bg-primary";
  return (
    <div className="rounded-xl border border-border/70 bg-card p-4 shadow-inner">
      <div className="flex items-center justify-between text-sm font-semibold">
        <span>{label}</span>
        <span className="text-muted-foreground">
          {stock}/{capacity}
        </span>
      </div>
      <div className="mt-3 h-2 rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${Math.min(100, ratio * 100)}%` }}
        />
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        {ratio < 0.35 ? "Rebuild buffer" : ratio > 0.9 ? "Risk of overstock" : "Balanced"}
      </p>
    </div>
  );
}

function StockTrend({ airport }: { airport: Airport }) {
  const lines = useMemo(() => {
    const total = airport.trend;
    return total.map((value, index) => ({
      step: index + 1,
      total: value,
      premium: value * 0.32 + index * 1.5,
      economy: value * 0.68 - index,
    }));
  }, [airport]);

  return (
    <Card className="glass">
      <CardHeader className="flex items-center justify-between pb-2">
        <div>
          <CardTitle>Stock over Time</CardTitle>
          <p className="text-sm text-muted-foreground">Class trends with buffers</p>
        </div>
        <Badge variant="muted">{lines.length} rounds</Badge>
      </CardHeader>
      <CardContent className="h-[260px]">
        <ResponsiveContainer>
          <LineChart data={lines}>
            <CartesianGrid strokeDasharray="4 4" stroke="hsl(var(--border))" />
            <XAxis dataKey="step" tickLine={false} axisLine={false} />
            <YAxis tickLine={false} axisLine={false} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="premium"
              stroke="#0ea5e9"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="economy"
              stroke="#f97316"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="total"
              stroke="#22c55e"
              strokeDasharray="4 4"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function FlowCard({ airport }: { airport: Airport }) {
  const flow = airport.inbound.map((inVal, idx) => ({
    idx,
    inbound: inVal,
    outbound: airport.outbound[idx] ?? 0,
  }));

  return (
    <Card className="glass">
      <CardHeader className="flex items-center justify-between pb-2">
        <div>
          <CardTitle>Flow outlook</CardTitle>
          <p className="text-sm text-muted-foreground">Inbound vs outbound kits</p>
        </div>
        <Badge variant="muted">{flow.length} hrs</Badge>
      </CardHeader>
      <CardContent className="h-[200px]">
        <ResponsiveContainer>
          <AreaChart data={flow} stackOffset="expand">
            <CartesianGrid strokeDasharray="4 4" stroke="hsl(var(--border))" />
            <XAxis dataKey="idx" tickLine={false} axisLine={false} />
            <YAxis tickFormatter={(val) => `${Math.round(val * 100)}%`} />
            <Tooltip
              formatter={(value: number, name: string) =>
                [`${value} kits`, name === "inbound" ? "Inbound" : "Outbound"]
              }
            />
            <Area
              type="monotone"
              dataKey="inbound"
              stackId="1"
              stroke="#0ea5e9"
              fill="#0ea5e9"
              fillOpacity={0.5}
            />
            <Area
              type="monotone"
              dataKey="outbound"
              stackId="1"
              stroke="#f97316"
              fill="#f97316"
              fillOpacity={0.5}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function UpcomingFlights({ airportCode }: { airportCode: string }) {
  const { data: flights = [] } = useQuery({
    queryKey: ["flights", airportCode],
    queryFn: () => fetchFlights({ airport: airportCode }),
  });

  const subset = flights.slice(0, 5);

  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <CardTitle>Upcoming flights</CardTitle>
        <p className="text-sm text-muted-foreground">Next few departures/arrivals</p>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>Flight</TableHead>
              <TableHead>Route</TableHead>
              <TableHead>Penalty</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {subset.map((flight) => (
              <TableRow key={flight.id} className="hover:bg-accent/40">
                <TableCell className="font-semibold">{flight.id}</TableCell>
                <TableCell>
                  {flight.origin} → {flight.destination}
                </TableCell>
                <TableCell className="text-sm">
                  <Badge>{flight.status}</Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {!subset.length ? (
          <p className="p-4 text-sm text-muted-foreground">
            No upcoming flights — great time to rebalance buffers.
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}

function AirportHeader({ airport }: { airport: Airport }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <MapPin className="h-5 w-5 text-primary" />
      <h2 className="text-xl font-semibold">
        {airport.code} · {airport.name}
      </h2>
      <Badge variant="muted">{airport.type}</Badge>
      {airport.tags?.map((tag) => (
        <Badge key={tag} variant="secondary">
          {tag}
        </Badge>
      ))}
    </div>
  );
}

function AirportsPage() {
  const { data: airportData = [] } = useQuery({
    queryKey: ["airports"],
    queryFn: fetchAirports,
  });
  const [selected, setSelected] = useState<string | null>(null);

  const current = useMemo(() => {
    if (!selected) return airportData[0];
    return airportData.find((a) => a.code === selected) ?? airportData[0];
  }, [selected, airportData]);

  if (!current) {
    return <p className="text-muted-foreground">Loading airports...</p>;
  }

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <AirportList airports={airportData} selected={current.code} onSelect={setSelected} />
      <div className="lg:col-span-2 space-y-4">
        <AirportHeader airport={current} />
        <div className="grid gap-3 md:grid-cols-2">
          {Object.keys(current.capacity).map((cabin) => (
            <CapacityCard
              key={cabin}
              label={cabin}
              capacity={current.capacity[cabin]}
              stock={current.stock[cabin]}
            />
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <StockTrend airport={current} />
          <FlowCard airport={current} />
        </div>
        <UpcomingFlights airportCode={current.code} />
        <div className="rounded-xl border border-border/70 bg-card p-4 text-sm text-muted-foreground shadow-inner">
          <div className="flex items-center gap-2">
            <PlaneLanding className="h-4 w-4 text-primary" />
            <span>Inbound buffers</span>
          </div>
          <p>
            Keep at least 25% premium coverage on inbound waves to avoid last-minute leasing.
          </p>
          <div className="mt-2 flex items-center gap-2">
            <PlaneTakeoff className="h-4 w-4 text-primary" />
            <span>Outbound guidance: {formatNumber(current.stock.Y)} Y kits available.</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AirportsPage;
