import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { Filter, Info, Plane, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Slider } from "@/components/ui/slider";
import { fetchAirports, fetchFlights } from "@/lib/api";
import type { FlightFilter, FlightRow } from "@/lib/types";
import { formatCost, statusColor } from "@/lib/utils";

function FilterBar({
  filters,
  setFilters,
  airports,
}: {
  filters: FlightFilter;
  setFilters: (next: FlightFilter) => void;
  airports: string[];
}) {
  return (
    <Card className="glass">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-primary" />
          <CardTitle>Filter flights</CardTitle>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() =>
            setFilters({ distance: [0, 14000], timeWindow: undefined, outcome: undefined, cabin: undefined, airport: undefined })
          }
        >
          Reset
        </Button>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-4">
        <div className="space-y-2">
          <Label>Airport</Label>
          <Select
            value={filters.airport ?? "all"}
            onValueChange={(value) =>
              setFilters({ ...filters, airport: value === "all" ? undefined : value })
            }
          >
            <SelectTrigger className="bg-card">
              <SelectValue placeholder="Select airport" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              {airports.map((code) => (
                <SelectItem key={code} value={code}>
                  {code}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Cabin</Label>
          <Select
            value={filters.cabin ?? "all"}
            onValueChange={(value) =>
              setFilters({ ...filters, cabin: value === "all" ? undefined : value })
            }
          >
            <SelectTrigger className="bg-card">
              <SelectValue placeholder="Cabin" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="F">First</SelectItem>
              <SelectItem value="J">Business</SelectItem>
              <SelectItem value="W">Premium</SelectItem>
              <SelectItem value="Y">Economy</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Outcome</Label>
          <Select
            value={filters.outcome ?? "all"}
            onValueChange={(value) =>
              setFilters({
                ...filters,
                outcome: value === "all" ? undefined : (value as FlightFilter["outcome"]),
              })
            }
          >
            <SelectTrigger className="bg-card">
              <SelectValue placeholder="Outcome" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="ok">Healthy</SelectItem>
              <SelectItem value="warning">Watch</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Distance (km)</Label>
          <Slider
            min={0}
            max={14000}
            step={500}
            value={filters.distance ?? [0, 14000]}
            onValueChange={(value) =>
              setFilters({ ...filters, distance: value as [number, number] })
            }
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{filters.distance?.[0] ?? 0}</span>
            <span>{filters.distance?.[1] ?? 14000}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function FlightDrawer({
  flight,
  onClose,
}: {
  flight: FlightRow | null;
  onClose: () => void;
}) {
  return (
    <AnimatePresence>
      {flight ? (
        <div className="fixed inset-0 z-40">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 320, damping: 32 }}
            className="absolute right-0 top-0 h-full w-full max-w-xl overflow-y-auto border-l border-border/70 bg-card shadow-2xl"
          >
            <div className="flex items-start justify-between border-b border-border/70 p-6">
              <div>
                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  Flight detail
                </p>
                <h3 className="text-xl font-semibold">
                  {flight.origin} → {flight.destination}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {flight.aircraft} · {flight.departure} — {flight.arrival}
                </p>
              </div>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-4 p-6">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl bg-secondary/80 p-3 shadow-inner">
                  <p className="text-muted-foreground">Operational cost</p>
                  <p className="text-lg font-semibold">
                    {formatCost(flight.operationalCost)}
                  </p>
                </div>
                <div className="rounded-xl bg-amber-500/10 p-3 shadow-inner">
                  <p className="text-muted-foreground">Penalties</p>
                  <p className="text-lg font-semibold text-amber-500">
                    {formatCost(flight.penaltyCost)}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {flight.cabins.map((cabin) => {
                  const served = (cabin.loaded / cabin.pax) * 100;
                  return (
                    <div
                      key={cabin.cabin}
                      className="rounded-xl border border-border/80 p-3 shadow-inner"
                    >
                      <div className="flex items-center justify-between text-sm font-semibold">
                        <span>{cabin.cabin}</span>
                        <Badge variant={served > 90 ? "success" : served > 70 ? "warning" : "danger"}>
                          {served.toFixed(0)}%
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Pax: {cabin.pax} · Kits: {cabin.loaded}
                      </p>
                      <p className="text-xs text-amber-500">
                        Penalty {formatCost(cabin.penalty * 15)}
                      </p>
                    </div>
                  );
                })}
              </div>
              <div className="rounded-xl bg-primary/10 p-4 text-sm text-primary-foreground">
                <p className="font-semibold text-primary">Why this happened</p>
                <p className="text-primary/90">{flight.explanation}</p>
              </div>
            </div>
          </motion.aside>
        </div>
      ) : null}
    </AnimatePresence>
  );
}

function FlightsTable({
  flightsData,
  onRowClick,
}: {
  flightsData: FlightRow[];
  onRowClick: (flight: FlightRow) => void;
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-border/70 bg-card shadow-card">
      <div className="max-h-[560px] overflow-y-auto">
        <Table>
          <TableHeader className="sticky top-0 bg-card/95 backdrop-blur">
            <TableRow className="hover:bg-transparent">
              <TableHead>Time</TableHead>
              <TableHead>Flight</TableHead>
              <TableHead>Distance</TableHead>
              <TableHead>Aircraft</TableHead>
              <TableHead>Cabins</TableHead>
              <TableHead>Operational</TableHead>
              <TableHead>Penalties</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {flightsData.map((flight) => (
              <TableRow
                key={flight.id}
                className="cursor-pointer hover:bg-accent/40"
                onClick={() => onRowClick(flight)}
              >
                <TableCell className="font-semibold">{flight.departure}</TableCell>
                <TableCell>
                  <div className="flex flex-col">
                    <span className="font-semibold text-foreground">
                      {flight.origin} → {flight.destination}
                    </span>
                    <span className="text-xs text-muted-foreground">{flight.id}</span>
                  </div>
                </TableCell>
                <TableCell>{flight.distance.toLocaleString()} km</TableCell>
                <TableCell>{flight.aircraft}</TableCell>
                <TableCell>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {flight.cabins.map((cabin) => {
                      const ratio = cabin.loaded / cabin.pax;
                      const color =
                        ratio > 0.9 ? "text-emerald-500" : ratio > 0.7 ? "text-amber-500" : "text-rose-500";
                      return (
                        <div key={cabin.cabin} className="flex items-center gap-1">
                          <span className={color}>●</span>
                          <span className="font-semibold">{cabin.cabin}</span>
                          <span className="text-muted-foreground">
                            {cabin.loaded}/{cabin.pax}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </TableCell>
                <TableCell>{formatCost(flight.operationalCost)}</TableCell>
                <TableCell>
                  <Badge className={statusColor(flight.status)}>
                    {flight.status === "ok" ? "Healthy" : flight.status === "warning" ? "Watch" : "Critical"}
                  </Badge>
                  <p className="text-xs text-muted-foreground">
                    {formatCost(flight.penaltyCost)}
                  </p>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

function FlightsPage() {
  const [filters, setFilters] = useState<FlightFilter>({ distance: [0, 14000] });
  const [selected, setSelected] = useState<FlightRow | null>(null);
  const { data: airportData = [] } = useQuery({
    queryKey: ["airports"],
    queryFn: fetchAirports,
  });
  const { data: flightsData, isLoading } = useQuery({
    queryKey: ["flights", filters],
    queryFn: () => fetchFlights(filters),
  });

  const airportCodes = useMemo(
    () => airportData.map((airport) => airport.code),
    [airportData],
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Plane className="h-5 w-5 text-primary" />
        <h1 className="text-2xl font-semibold">Flights & Simulation</h1>
        <Badge variant="muted" className="ml-2">
          Table view
        </Badge>
      </div>
      <FilterBar filters={filters} setFilters={setFilters} airports={airportCodes} />

      {isLoading ? (
        <Skeleton className="h-[420px] rounded-2xl" />
      ) : flightsData && flightsData.length ? (
        <FlightsTable flightsData={flightsData} onRowClick={setSelected} />
      ) : (
        <Card className="glass">
          <CardContent className="flex items-center gap-3 p-6">
            <Info className="h-5 w-5 text-primary" />
            <div>
              <p className="font-semibold">No flights match your filters.</p>
              <p className="text-sm text-muted-foreground">
                Try expanding the distance range or clearing the outcome filter.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      <FlightDrawer flight={selected} onClose={() => setSelected(null)} />
    </div>
  );
}

export default FlightsPage;
