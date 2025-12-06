from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FLIGHTS_CSV = ROOT / "data" / "flights.csv"
AIRCRAFT_CSV = ROOT / "data" / "aircraft_types.csv"
IMG_DIR = Path(__file__).resolve().parent / "imgs"
SUMMARY_CSV = Path(__file__).resolve().parent / "flight_kits_vs_capacity_summary.csv"

CLASS_COLS = {
    "first": ("actual_first_passengers", "first_class_kits_capacity"),
    "business": ("actual_business_passengers", "business_kits_capacity"),
    "premiumEconomy": ("actual_premium_economy_passengers", "premium_economy_kits_capacity"),
    "economy": ("actual_economy_passengers", "economy_kits_capacity"),
}


def load_data() -> pd.DataFrame:
    flights = pd.read_csv(FLIGHTS_CSV, sep=";")
    aircraft = pd.read_csv(AIRCRAFT_CSV, sep=";")

    aircraft_caps = aircraft.set_index("id")[
        [v[1] for v in CLASS_COLS.values()]
    ]

    # prefer actual aircraft type when available
    flights["aircraft_id_used"] = flights["act_aircraft_type_id"].fillna(flights["sched_aircraft_type_id"])
    merged = flights.join(aircraft_caps, on="aircraft_id_used", how="left", rsuffix="_cap")
    return merged


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cls, (pax_col, cap_col) in CLASS_COLS.items():
        subset = df[[pax_col, cap_col]].dropna()
        subset = subset[subset[cap_col] > 0]
        if subset.empty:
            continue
        subset = subset.assign(utilization=subset[pax_col] / subset[cap_col])
        rows.append(
            {
                "class": cls,
                "avg_kits_needed": subset[pax_col].mean(),
                "median_kits_needed": subset[pax_col].median(),
                "max_kits_needed": subset[pax_col].max(),
                "avg_capacity": subset[cap_col].mean(),
                "avg_utilization": subset["utilization"].mean(),
                "p95_utilization": subset["utilization"].quantile(0.95),
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(SUMMARY_CSV, index=False)
    return summary


def plot_utilization(df: pd.DataFrame) -> Path:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()

    for ax, (cls, (pax_col, cap_col)) in zip(axes, CLASS_COLS.items()):
        subset = df[[pax_col, cap_col]].dropna()
        subset = subset[subset[cap_col] > 0]
        if subset.empty:
            ax.set_visible(False)
            continue
        util = subset[pax_col] / subset[cap_col]
        ax.hist(util, bins=30, color="#4C72B0", edgecolor="white", alpha=0.85)
        ax.set_title(f"{cls} utilization (pax / kit capacity)")
        ax.set_xlabel("Utilization")
        ax.set_ylabel("Flights")
        ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    out_path = IMG_DIR / "flight_utilization_hist.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_kits_needed(df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()

    for ax, (cls, (pax_col, _)) in zip(axes, CLASS_COLS.items()):
        if pax_col not in df:
            ax.set_visible(False)
            continue
        ax.hist(df[pax_col].dropna(), bins=30, color="#55A868", edgecolor="white", alpha=0.85)
        ax.set_title(f"{cls} actual kits needed (pax)")
        ax.set_xlabel("Kits")
        ax.set_ylabel("Flights")
        ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    out_path = IMG_DIR / "kits_needed_hist.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def main() -> None:
    df = load_data()
    summary = summarize(df)
    util_img = plot_utilization(df)
    kits_img = plot_kits_needed(df)
    print("Saved summary to", SUMMARY_CSV)
    print(summary)
    print("Saved utilization histogram to", util_img)
    print("Saved kits-needed histogram to", kits_img)


if __name__ == "__main__":
    main()
