import {
  airports,
  baseStrategyParams,
  buildDashboardPayload,
  comparisonResults,
  flights,
  scenarios,
  strategySummaries,
} from "./mock-data";
import type {
  Airport,
  DashboardPayload,
  FlightFilter,
  FlightRow,
  Scenario,
  SimulationResult,
  StrategyParams,
  StrategySummary,
} from "./types";

const wait = (ms = 220) => new Promise((resolve) => setTimeout(resolve, ms));

const fuzzyMatch = (value: number, range?: [number, number]) => {
  if (!range) return true;
  return value >= range[0] && value <= range[1];
};

export async function fetchScenarios(): Promise<Scenario[]> {
  await wait();
  return scenarios;
}

export async function fetchScenarioSummary(id: string): Promise<StrategySummary> {
  await wait(120);
  return strategySummaries[id] ?? strategySummaries.baseline;
}

export async function fetchDashboard(
  scenarioId: string,
): Promise<DashboardPayload> {
  await wait();
  return buildDashboardPayload(scenarioId);
}

export async function fetchFlights(
  filters?: FlightFilter,
): Promise<FlightRow[]> {
  await wait();
  if (!filters) return flights;

  return flights.filter((flight) => {
    const airportPass =
      !filters.airport ||
      flight.origin === filters.airport ||
      flight.destination === filters.airport;
    const cabinPass =
      !filters.cabin ||
      flight.cabins.some((c) => c.cabin.toUpperCase() === filters.cabin);
    const distancePass = fuzzyMatch(flight.distance, filters.distance);
    const outcomePass = !filters.outcome || flight.status === filters.outcome;
    return airportPass && cabinPass && distancePass && outcomePass;
  });
}

export async function fetchAirports(): Promise<Airport[]> {
  await wait();
  return airports;
}

export async function fetchAirportDetail(code: string): Promise<Airport> {
  await wait(180);
  const airport = airports.find((a) => a.code === code);
  if (!airport) {
    throw new Error("Airport not found");
  }
  return airport;
}

export async function fetchStrategyParams(): Promise<StrategyParams> {
  await wait(100);
  return baseStrategyParams;
}

export async function runSimulation(
  params: StrategyParams,
): Promise<{ baseline: SimulationResult; current: SimulationResult }> {
  await wait(420);

  const premiumLift =
    (params.biases.F - 1.2) * 0.06 + (params.biases.J - 1.1) * 0.04;
  const econThrottle = params.holdOnLong.Y ? 0.08 : 0.03;
  const penaltyScale = Math.max(0.68, 0.92 - premiumLift - econThrottle);
  const operationalScale = Math.max(
    0.9,
    1 + (params.biases.F - 1.2) * 0.05 + (params.biases.J - 1.1) * 0.03,
  );

  const baseline = comparisonResults[0];
  const tuned: SimulationResult = {
    name: "Tuned",
    totalCost: Math.round(
      comparisonResults[1].totalCost * operationalScale +
        comparisonResults[1].penalties * penaltyScale,
    ),
    operational: Math.round(comparisonResults[1].operational * operationalScale),
    penalties: Math.round(comparisonResults[1].penalties * penaltyScale),
    penaltyBreakdown: comparisonResults[1].penaltyBreakdown.map((slice) => ({
      ...slice,
      value: Math.round(slice.value * penaltyScale),
    })),
    insight:
      "Tuned mix prioritizes premium cabins and trims long-haul economy; penalties fall while cost stays in check.",
  };

  return { baseline, current: tuned };
}
