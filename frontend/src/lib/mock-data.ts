import type {
  Airport,
  CostPoint,
  DashboardPayload,
  FlightRow,
  PenaltySlice,
  Scenario,
  SimulationResult,
  StrategyParams,
  StrategySummary,
  NetworkNode,
} from "./types";

export const scenarios: Scenario[] = [
  {
    id: "baseline",
    name: "Baseline",
    description: "Even allocation policy without cost awareness.",
    tag: "Reference",
    mode: "Deterministic",
    updatedAt: "12 min ago",
  },
  {
    id: "costAware",
    name: "Cost-Aware Heuristic",
    description: "Penalty-aware thresholding with premium class bias.",
    tag: "Live",
    mode: "Heuristic",
    updatedAt: "3 min ago",
  },
  {
    id: "distance",
    name: "Distance-Averse FC-Priority",
    description: "Avoids long-haul economy moves while protecting FC/Business.",
    tag: "Aggressive",
    mode: "Exploratory",
    updatedAt: "just now",
  },
];

export const baseCostSeries: CostPoint[] = [
  { round: 1, operational: 16253, penalty: 27, total: 16280 },
  { round: 2, operational: 18336, penalty: 24, total: 18360 },
  { round: 3, operational: 13811, penalty: 23, total: 13834 },
  { round: 4, operational: 9351, penalty: 11, total: 9361 },
  { round: 5, operational: 13802, penalty: 22, total: 13824 },
  { round: 6, operational: 14138, penalty: 22, total: 14160 },
  { round: 7, operational: 13573, penalty: 18, total: 13592 },
  { round: 8, operational: 17852, penalty: 38, total: 17889 },
  { round: 9, operational: 18321, penalty: 23, total: 18344 },
  { round: 10, operational: 13762, penalty: 25, total: 13787 },
  { round: 11, operational: 9341, penalty: 17, total: 9357 },
  { round: 12, operational: 13758, penalty: 23, total: 13781 },
];

export const basePenaltyBreakdown: PenaltySlice[] = [
  { type: "Economy unserved", value: 42325, color: "#38bdf8" },
  { type: "Premium Economy unserved", value: 3343, color: "#22c55e" },
  { type: "Business unserved", value: 2749, color: "#f97316" },
  { type: "First unserved", value: 1565, color: "#a855f7" },
  { type: "Other adjustments", value: 620, color: "#eab308" },
];

export const networkNodes: NetworkNode[] = [
  {
    code: "HUB1",
    name: "Main Hub Airport",
    region: "Core",
    stock: 1659 + 5184 + 2668 + 23651,
    capacity: 18109 + 18109 + 9818 + 95075,
    imbalance: -1200,
    x: 0.1,
    y: 0.2,
    risk: "low",
  },
  {
    code: "ZHVK",
    name: "Airport ZHVK",
    region: "Regional",
    stock: 158 + 105 + 135 + 304,
    capacity: 445 + 445 + 290 + 803,
    imbalance: -90,
    x: 0.18,
    y: 0.2,
    risk: "low",
  },
  {
    code: "WPUE",
    name: "Airport WPUE",
    region: "Regional",
    stock: 136 + 189 + 127 + 581,
    capacity: 496 + 496 + 319 + 1408,
    imbalance: -70,
    x: 0.26,
    y: 0.2,
    risk: "low",
  },
  {
    code: "UIVJ",
    name: "Airport UIVJ",
    region: "Regional",
    stock: 144 + 110 + 105 + 412,
    capacity: 428 + 428 + 293 + 975,
    imbalance: -40,
    x: 0.34,
    y: 0.2,
    risk: "low",
  },
  {
    code: "EEUQ",
    name: "Airport EEUQ",
    region: "Regional",
    stock: 150 + 144 + 144 + 168,
    capacity: 264 + 264 + 397 + 632,
    imbalance: -60,
    x: 0.1,
    y: 0.35,
    risk: "low",
  },
  {
    code: "ZDQP",
    name: "Airport ZDQP",
    region: "Regional",
    stock: 119 + 100 + 99 + 187,
    capacity: 525 + 525 + 305 + 825,
    imbalance: -120,
    x: 0.18,
    y: 0.35,
    risk: "low",
  },
  {
    code: "KLZQ",
    name: "Airport KLZQ",
    region: "Regional",
    stock: 122 + 104 + 92 + 121,
    capacity: 399 + 399 + 363 + 544,
    imbalance: -80,
    x: 0.26,
    y: 0.35,
    risk: "low",
  },
  {
    code: "INFQ",
    name: "Airport INFQ",
    region: "Regional",
    stock: 138 + 182 + 104 + 298,
    capacity: 424 + 424 + 317 + 1762,
    imbalance: -50,
    x: 0.34,
    y: 0.35,
    risk: "low",
  },
];

export const networkEdges = [
  { from: "HUB1", to: "ZHVK", volume: 64 },
  { from: "HUB1", to: "WPUE", volume: 42 },
  { from: "HUB1", to: "UIVJ", volume: 38 },
  { from: "HUB1", to: "EEUQ", volume: 26 },
  { from: "ZHVK", to: "HUB1", volume: 58 },
  { from: "WPUE", to: "HUB1", volume: 40 },
  { from: "UIVJ", to: "HUB1", volume: 32 },
  { from: "ZDQP", to: "HUB1", volume: 24 },
];

export const strategySummaries: Record<string, StrategySummary> = {
  baseline: {
    title: "Baseline",
    description: "Greedy allocation without cost sensitivity; relies on proximity.",
    chips: ["Neutral bias", "Distance only", "No penalty shaping"],
    rules: [
      "Allocate kits to earliest flights first",
      "No class-level prioritization",
      "Minimal validation on negative inventory",
    ],
  },
  costAware: {
    title: "Cost-Aware Heuristic",
    description:
      "Balances marginal penalty vs operational spend; favors premium cabins and keeps buffers at hubs.",
    chips: ["Premium bias", "Penalty-first on long-haul", "Hub buffers"],
    rules: [
      "Block Economy if penalty < cost * 0.75 on >3200km",
      "Push FC/Business to 95% coverage before others",
      "Cap outbound stock at 90% to protect hub buffers",
    ],
  },
  distance: {
    title: "Distance-Averse FC-Priority",
    description:
      "Reduces long-haul kit movement; aggressive FC/Business priority with distance-aware throttling.",
    chips: ["FC hard-priority", "Distance gating", "Penalty smoothing"],
    rules: [
      "Route FC/Business first on all flights",
      "Throttle Economy on >2800km unless penalty > cost * 1.2",
      "Prefer rebalancing to hubs before outstations",
    ],
  },
};

export const flights: FlightRow[] = [
  {
    id: "AB1000",
    origin: "HUB1",
    destination: "ZHVK",
    distance: 736,
    aircraft: "A/C",
    departure: "15:00",
    arrival: "16:00",
    operationalCost: 16192,
    penaltyCost: 300,
    cabins: [
      { cabin: "F", pax: 20, loaded: 20, penalty: 0 },
      { cabin: "J", pax: 1, loaded: 1, penalty: 0 },
      { cabin: "W", pax: 28, loaded: 28, penalty: 0 },
      { cabin: "Y", pax: 163, loaded: 143, penalty: 20 },
    ],
    status: "warning",
    explanation: "Gap between planned and loaded kits reflected as penalty surrogate.",
  },
  {
    id: "AB1000",
    origin: "HUB1",
    destination: "ZHVK",
    distance: 736,
    aircraft: "A/C",
    departure: "15:00",
    arrival: "16:00",
    operationalCost: 16192,
    penaltyCost: 0,
    cabins: [
      { cabin: "F", pax: 6, loaded: 6, penalty: 0 },
      { cabin: "J", pax: 31, loaded: 32, penalty: 0 },
      { cabin: "W", pax: 14, loaded: 15, penalty: 0 },
      { cabin: "Y", pax: 265, loaded: 312, penalty: 0 },
    ],
    status: "ok",
    explanation: "All cabins served",
  },
  {
    id: "AB1000",
    origin: "HUB1",
    destination: "ZHVK",
    distance: 736,
    aircraft: "A/C",
    departure: "15:00",
    arrival: "16:00",
    operationalCost: 16192,
    penaltyCost: 225,
    cabins: [
      { cabin: "F", pax: 13, loaded: 13, penalty: 0 },
      { cabin: "J", pax: 63, loaded: 62, penalty: 1 },
      { cabin: "W", pax: 17, loaded: 15, penalty: 2 },
      { cabin: "Y", pax: 109, loaded: 97, penalty: 12 },
    ],
    status: "warning",
    explanation: "Gap between planned and loaded kits reflected as penalty surrogate.",
  },
  {
    id: "AB1000",
    origin: "HUB1",
    destination: "ZHVK",
    distance: 758,
    aircraft: "A/C",
    departure: "15:00",
    arrival: "16:00",
    operationalCost: 16676,
    penaltyCost: 75,
    cabins: [
      { cabin: "F", pax: 1, loaded: 1, penalty: 0 },
      { cabin: "J", pax: 37, loaded: 38, penalty: 0 },
      { cabin: "W", pax: 14, loaded: 15, penalty: 0 },
      { cabin: "Y", pax: 116, loaded: 111, penalty: 5 },
    ],
    status: "warning",
    explanation: "Gap between planned and loaded kits reflected as penalty surrogate.",
  },
  {
    id: "AB1000",
    origin: "HUB1",
    destination: "ZHVK",
    distance: 736,
    aircraft: "A/C",
    departure: "15:00",
    arrival: "16:00",
    operationalCost: 16192,
    penaltyCost: 165,
    cabins: [
      { cabin: "F", pax: 6, loaded: 6, penalty: 0 },
      { cabin: "J", pax: 21, loaded: 21, penalty: 0 },
      { cabin: "W", pax: 6, loaded: 6, penalty: 0 },
      { cabin: "Y", pax: 77, loaded: 66, penalty: 11 },
    ],
    status: "warning",
    explanation: "Gap between planned and loaded kits reflected as penalty surrogate.",
  },
  {
    id: "AB1001",
    origin: "ZHVK",
    destination: "HUB1",
    distance: 2946,
    aircraft: "A/C",
    departure: "21:00",
    arrival: "01:00",
    operationalCost: 64812,
    penaltyCost: 90,
    cabins: [
      { cabin: "F", pax: 6, loaded: 6, penalty: 0 },
      { cabin: "J", pax: 54, loaded: 55, penalty: 0 },
      { cabin: "W", pax: 14, loaded: 14, penalty: 0 },
      { cabin: "Y", pax: 52, loaded: 46, penalty: 6 },
    ],
    status: "warning",
    explanation: "Gap between planned and loaded kits reflected as penalty surrogate.",
  },
  {
    id: "AB1001",
    origin: "ZHVK",
    destination: "HUB1",
    distance: 2946,
    aircraft: "A/C",
    departure: "21:00",
    arrival: "01:00",
    operationalCost: 64812,
    penaltyCost: 0,
    cabins: [
      { cabin: "F", pax: 0, loaded: 0, penalty: 0 },
      { cabin: "J", pax: 9, loaded: 9, penalty: 0 },
      { cabin: "W", pax: 3, loaded: 3, penalty: 0 },
      { cabin: "Y", pax: 127, loaded: 150, penalty: 0 },
    ],
    status: "ok",
    explanation: "All cabins served",
  },
  {
    id: "AB1001",
    origin: "ZHVK",
    destination: "HUB1",
    distance: 3152,
    aircraft: "A/C",
    departure: "21:00",
    arrival: "01:00",
    operationalCost: 69344,
    penaltyCost: 0,
    cabins: [
      { cabin: "F", pax: 6, loaded: 6, penalty: 0 },
      { cabin: "J", pax: 45, loaded: 45, penalty: 0 },
      { cabin: "W", pax: 14, loaded: 14, penalty: 0 },
      { cabin: "Y", pax: 164, loaded: 172, penalty: 0 },
    ],
    status: "ok",
    explanation: "All cabins served",
  },
];

export const airports: Airport[] = [
  {
    code: "HUB1",
    name: "Main Hub Airport",
    type: "Hub",
    capacity: { F: 18109, J: 18109, W: 9818, Y: 95075 },
    stock: { F: 1659, J: 5184, W: 2668, Y: 23651 },
    trend: [5200, 5400, 5600, 6000, 6200, 6400, 6800, 7100, 7300, 7600],
    inbound: [420, 380, 450, 460, 500, 520],
    outbound: [360, 340, 410, 390, 430, 440],
    tags: ["Primary hub", "Low risk"],
  },
  {
    code: "ZHVK",
    name: "Airport ZHVK",
    type: "Outstation",
    capacity: { F: 445, J: 445, W: 290, Y: 803 },
    stock: { F: 158, J: 105, W: 135, Y: 304 },
    trend: [220, 240, 260, 255, 270, 280, 290, 300, 304, 310],
    inbound: [38, 32, 28, 30, 34, 36],
    outbound: [36, 34, 32, 30, 28, 26],
    tags: ["Feeder", "Economy-heavy"],
  },
  {
    code: "WPUE",
    name: "Airport WPUE",
    type: "Outstation",
    capacity: { F: 496, J: 496, W: 319, Y: 1408 },
    stock: { F: 136, J: 189, W: 127, Y: 581 },
    trend: [260, 270, 285, 300, 310, 320, 340, 360, 370, 390],
    inbound: [36, 32, 40, 38, 34, 42],
    outbound: [30, 36, 34, 32, 30, 28],
    tags: ["Steady", "Mixed cabins"],
  },
  {
    code: "UIVJ",
    name: "Airport UIVJ",
    type: "Outstation",
    capacity: { F: 428, J: 428, W: 293, Y: 975 },
    stock: { F: 144, J: 110, W: 105, Y: 412 },
    trend: [230, 240, 250, 255, 262, 270, 280, 292, 300, 310],
    inbound: [28, 30, 32, 26, 30, 34],
    outbound: [24, 26, 28, 30, 32, 28],
    tags: ["Stable", "Premium buffer"],
  },
  {
    code: "ZDQP",
    name: "Airport ZDQP",
    type: "Outstation",
    capacity: { F: 525, J: 525, W: 305, Y: 825 },
    stock: { F: 119, J: 100, W: 99, Y: 187 },
    trend: [180, 182, 184, 186, 188, 190, 192, 194, 196, 198],
    inbound: [20, 22, 24, 26, 20, 18],
    outbound: [16, 18, 20, 20, 18, 16],
    tags: ["Lean", "Watch stock"],
  },
];

export const baseStrategyParams: StrategyParams = {
  biases: { F: 1.2, J: 1.1, W: 0.95, Y: 0.8 },
  distanceThresholds: { short: 1200, medium: 3200, long: 7200 },
  costAlpha: { F: 1.25, J: 1.1, W: 0.9, Y: 0.75 },
  holdOnLong: { F: false, J: false, W: true, Y: true },
  episodes: 6,
  seed: 42,
};

export const comparisonResults: SimulationResult[] = [
  {
    name: "Baseline",
    totalCost: 438_917_636,
    operational: 438_167_906,
    penalties: 749_730,
    penaltyBreakdown: basePenaltyBreakdown,
    insight: "Baseline keeps movements simple but absorbs large economy penalties on long-haul.",
  },
  {
    name: "Current",
    totalCost: 418_100_000,
    operational: 432_000_000,
    penalties: 610_000,
    penaltyBreakdown: [
      { type: "Economy unserved", value: 36200, color: "#38bdf8" },
      { type: "Premium Economy unserved", value: 3200, color: "#22c55e" },
      { type: "Business unserved", value: 2400, color: "#f97316" },
      { type: "First unserved", value: 1300, color: "#a855f7" },
      { type: "Other adjustments", value: 540, color: "#eab308" },
    ],
    insight: "Penalty-aware tuning trims unserved cabins while keeping operational spend close to baseline.",
  },
];

export const dashboardHighlights: Record<string, string> = {
  baseline: "Penalties spike on long-haul economy; feeders lean on HUB1 buffers.",
  costAware: "Premium cabins protected; penalties trimmed with modest operational shift.",
  distance: "Distance gating slashes penalties; watch lean outstations like ZDQP.",
};

export const scenarioCostAdjustments: Record<
  string,
  { operational: number; penalty: number }
> = {
  baseline: { operational: 1, penalty: 1 },
  costAware: { operational: 0.98, penalty: 0.82 },
  distance: { operational: 0.97, penalty: 0.76 },
};

export const scenarioPenaltyBreakdown: Record<string, PenaltySlice[]> = {
  baseline: basePenaltyBreakdown,
  costAware: [
    { type: "Economy unserved", value: 36200, color: "#38bdf8" },
    { type: "Premium Economy unserved", value: 3200, color: "#22c55e" },
    { type: "Business unserved", value: 2400, color: "#f97316" },
    { type: "First unserved", value: 1300, color: "#a855f7" },
    { type: "Other adjustments", value: 540, color: "#eab308" },
  ],
  distance: [
    { type: "Economy unserved", value: 31000, color: "#38bdf8" },
    { type: "Premium Economy unserved", value: 2900, color: "#22c55e" },
    { type: "Business unserved", value: 2100, color: "#f97316" },
    { type: "First unserved", value: 1200, color: "#a855f7" },
    { type: "Other adjustments", value: 520, color: "#eab308" },
  ],
};

export const dashboardKpis: Record<string, DashboardPayload["kpis"]> = {
  baseline: [
    { label: "Total Cost", value: 438_917_636, delta: 0, unit: "cost" },
    { label: "Operational Cost", value: 438_167_906, delta: 0, unit: "cost" },
    { label: "Penalties", value: 749_730, delta: 0, unit: "cost" },
    { label: "Avg Cost / Flight", value: 60_233, delta: 0, unit: "cost" },
  ],
  costAware: [
    { label: "Total Cost", value: 418_100_000, delta: -4.8, unit: "cost" },
    { label: "Operational Cost", value: 432_000_000, delta: -1.4, unit: "cost" },
    { label: "Penalties", value: 610_000, delta: -18.6, unit: "cost" },
    { label: "Avg Cost / Flight", value: 57_375, delta: -4.7, unit: "cost" },
  ],
  distance: [
    { label: "Total Cost", value: 409_500_000, delta: -6.7, unit: "cost" },
    { label: "Operational Cost", value: 430_000_000, delta: -1.9, unit: "cost" },
    { label: "Penalties", value: 520_000, delta: -30.7, unit: "cost" },
    { label: "Avg Cost / Flight", value: 56_200, delta: -6.7, unit: "cost" },
  ],
};

export function buildDashboardPayload(scenarioId: string): DashboardPayload {
  const multiplier = scenarioCostAdjustments[scenarioId] ?? scenarioCostAdjustments.baseline;
  const series = baseCostSeries.map((point) => {
    const operational = Math.round(point.operational * multiplier.operational);
    const penalty = Math.round(point.penalty * multiplier.penalty);
    return {
      round: point.round,
      operational,
      penalty,
      total: operational + penalty,
    };
  });

  return {
    kpis: dashboardKpis[scenarioId] ?? dashboardKpis.baseline,
    costSeries: series,
    penaltyBreakdown: scenarioPenaltyBreakdown[scenarioId] ?? basePenaltyBreakdown,
    network: { nodes: networkNodes, edges: networkEdges },
    strategy: strategySummaries[scenarioId] ?? strategySummaries.baseline,
    highlight: dashboardHighlights[scenarioId] ?? dashboardHighlights.baseline,
  };
}
