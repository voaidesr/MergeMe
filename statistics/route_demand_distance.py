from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FLIGHTS_CSV = ROOT / "data" / "flights.csv"
AIRPORTS_CSV = ROOT / "data" / "airports_with_stocks.csv"
IMG_DIR = Path(__file__).resolve().parent / "imgs"
SUMMARY_CSV = Path(__file__).resolve().parent / "route_demand_distance_summary.csv"


def load_data() -> pd.DataFrame:
    flights = pd.read_csv(FLIGHTS_CSV, sep=";")
    airports = pd.read_csv(AIRPORTS_CSV, sep=";")[["id", "code"]].set_index("id")["code"]

    flights["origin_code"] = flights["origin_airport_id"].map(airports)
    flights["dest_code"] = flights["destination_airport_id"].map(airports)
    flights["actual_total_pax"] = (
        flights["actual_first_passengers"]
        + flights["actual_business_passengers"]
        + flights["actual_premium_economy_passengers"]
        + flights["actual_economy_passengers"]
    )
    flights["planned_total_pax"] = (
        flights["planned_first_passengers"]
        + flights["planned_business_passengers"]
        + flights["planned_premium_economy_passengers"]
        + flights["planned_economy_passengers"]
    )
    return flights


def summarize(flights: pd.DataFrame) -> pd.DataFrame:
    grouped = flights.groupby(["origin_code", "dest_code"])
    summary = grouped.agg(
        flights=("id", "count"),
        avg_actual_pax=("actual_total_pax", "mean"),
        median_actual_pax=("actual_total_pax", "median"),
        avg_planned_pax=("planned_total_pax", "mean"),
        avg_distance=("actual_distance", "mean"),
        median_distance=("actual_distance", "median"),
    ).reset_index()
    summary.to_csv(SUMMARY_CSV, index=False)
    return summary


def plot_total_pax_hist(flights: pd.DataFrame) -> Path:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(flights["actual_total_pax"].dropna(), bins=40, color="#4C72B0", edgecolor="white", alpha=0.85)
    ax.set_title("Actual total passengers per flight")
    ax.set_xlabel("Passengers (kits needed)")
    ax.set_ylabel("Flights")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    out_path = IMG_DIR / "total_pax_per_flight_hist.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_distance_hist(flights: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(flights["actual_distance"].dropna(), bins=40, color="#55A868", edgecolor="white", alpha=0.85)
    ax.set_title("Actual distance per flight (km)")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Flights")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    out_path = IMG_DIR / "distance_per_flight_hist.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_top_routes(summary: pd.DataFrame, top_n: int = 15) -> Path:
    top = summary.nlargest(top_n, "avg_actual_pax")
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = top.apply(lambda r: f"{r['origin_code']}→{r['dest_code']}", axis=1)
    ax.barh(labels, top["avg_actual_pax"], color="#C44E52")
    ax.invert_yaxis()
    ax.set_title(f"Top {top_n} routes by avg actual passengers")
    ax.set_xlabel("Average passengers (kits)")
    for i, v in enumerate(top["avg_actual_pax"]):
        ax.text(v + 1, i, f"{v:.1f}", va="center")
    plt.tight_layout()
    out_path = IMG_DIR / "top_routes_by_pax.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def main() -> None:
    flights = load_data()
    summary = summarize(flights)
    pax_hist = plot_total_pax_hist(flights)
    dist_hist = plot_distance_hist(flights)
    top_routes_img = plot_top_routes(summary)
    print("Saved summary to", SUMMARY_CSV)
    print(summary.head())
    print("Saved total pax histogram to", pax_hist)
    print("Saved distance histogram to", dist_hist)
    print("Saved top routes chart to", top_routes_img)


if __name__ == "__main__":
    main()
