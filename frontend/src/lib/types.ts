export type Scenario = {
  id: string;
  name: string;
  description: string;
  tag?: string;
  mode: string;
  updatedAt: string;
};

export type KPI = {
  label: string;
  value: number;
  unit?: string;
  delta?: number;
  helper?: string;
};

export type CostPoint = {
  round: number;
  operational: number;
  penalty: number;
  total: number;
};

export type PenaltySlice = {
  type: string;
  value: number;
  color?: string;
};

export type NetworkNode = {
  code: string;
  name: string;
  region: string;
  stock: number;
  capacity: number;
  imbalance: number;
  x: number;
  y: number;
  risk: "low" | "medium" | "high";
};

export type NetworkEdge = {
  from: string;
  to: string;
  volume: number;
};

export type StrategySummary = {
  title: string;
  description: string;
  chips: string[];
  rules: string[];
};

export type DashboardPayload = {
  kpis: KPI[];
  costSeries: CostPoint[];
  penaltyBreakdown: PenaltySlice[];
  network: {
    nodes: NetworkNode[];
    edges: NetworkEdge[];
  };
  strategy: StrategySummary;
  highlight: string;
};

export type FlightCabin = {
  cabin: string;
  pax: number;
  loaded: number;
  penalty: number;
};

export type FlightRow = {
  id: string;
  origin: string;
  destination: string;
  distance: number;
  aircraft: string;
  departure: string;
  arrival: string;
  operationalCost: number;
  penaltyCost: number;
  cabins: FlightCabin[];
  status: "ok" | "warning" | "critical";
  explanation: string;
};

export type FlightFilter = {
  airport?: string;
  distance?: [number, number];
  cabin?: string;
  timeWindow?: [number, number];
  outcome?: "ok" | "warning" | "critical";
};

export type Airport = {
  code: string;
  name: string;
  type: "Hub" | "Outstation";
  capacity: Record<string, number>;
  stock: Record<string, number>;
  trend: number[];
  inbound: number[];
  outbound: number[];
  tags?: string[];
};

export type StrategyParams = {
  biases: Record<string, number>;
  distanceThresholds: {
    short: number;
    medium: number;
    long: number;
  };
  costAlpha: Record<string, number>;
  holdOnLong: Record<string, boolean>;
  episodes: number;
  seed: number;
};

export type SimulationResult = {
  name: string;
  totalCost: number;
  operational: number;
  penalties: number;
  penaltyBreakdown: PenaltySlice[];
  insight: string;
};
