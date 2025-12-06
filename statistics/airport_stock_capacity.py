from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
AIRPORTS_CSV = ROOT / "data" / "airports_with_stocks.csv"
IMG_DIR = Path(__file__).resolve().parent / "imgs"
SUMMARY_CSV = Path(__file__).resolve().parent / "airport_stock_capacity_summary.csv"

CLASS_STOCK_COLS = {
    "first": "initial_fc_stock",
    "business": "initial_bc_stock",
    "premiumEconomy": "initial_pe_stock",
    "economy": "initial_ec_stock",
}

CLASS_CAP_COLS = {
    "first": "capacity_fc",
    "business": "capacity_bc",
    "premiumEconomy": "capacity_pe",
    "economy": "capacity_ec",
}


def load_data() -> pd.DataFrame:
    return pd.read_csv(AIRPORTS_CSV, sep=";")


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    per_airport = []
    for _, row in df.iterrows():
        total_stock = sum(row[CLASS_STOCK_COLS[c]] for c in CLASS_STOCK_COLS)
        total_cap = sum(row[CLASS_CAP_COLS[c]] for c in CLASS_CAP_COLS)
        per_airport.append(
            {
                "code": row["code"],
                "name": row["name"],
                "total_stock": total_stock,
                "total_capacity": total_cap,
                "stock_capacity_ratio": total_stock / total_cap if total_cap else 0,
                **{
                    f"{c}_stock": row[CLASS_STOCK_COLS[c]] for c in CLASS_STOCK_COLS
                },
                **{
                    f"{c}_capacity": row[CLASS_CAP_COLS[c]] for c in CLASS_CAP_COLS
                },
                **{
                    f"{c}_ratio": (row[CLASS_STOCK_COLS[c]] / row[CLASS_CAP_COLS[c]])
                    if row[CLASS_CAP_COLS[c]]
                    else 0
                    for c in CLASS_STOCK_COLS
                },
            }
        )
    summary = pd.DataFrame(per_airport)
    summary.to_csv(SUMMARY_CSV, index=False)
    return summary


def plot_ratios(summary: pd.DataFrame) -> Path:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(summary["stock_capacity_ratio"], bins=30, color="#4C72B0", edgecolor="white", alpha=0.85)
    ax.set_title("Airport total stock / capacity ratio")
    ax.set_xlabel("Ratio")
    ax.set_ylabel("Airports")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    out_path = IMG_DIR / "airport_stock_capacity_ratio_hist.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_tight_airports(summary: pd.DataFrame, top_n: int = 15) -> Path:
    tight = summary.nsmallest(top_n, "stock_capacity_ratio")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(tight["code"], tight["stock_capacity_ratio"], color="#55A868")
    ax.set_title(f"Tightest airports by stock/capacity ratio (top {top_n})")
    ax.set_xlabel("Stock / Capacity")
    ax.invert_yaxis()
    for i, v in enumerate(tight["stock_capacity_ratio"]):
        ax.text(v + 0.01, i, f"{v:.2f}", va="center")
    plt.tight_layout()
    out_path = IMG_DIR / "airport_stock_capacity_tight.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def main() -> None:
    df = load_data()
    summary = summarize(df)
    ratio_img = plot_ratios(summary)
    tight_img = plot_tight_airports(summary)
    print("Saved summary to", SUMMARY_CSV)
    print(summary.head())
    print("Saved ratio histogram to", ratio_img)
    print("Saved tight-airport chart to", tight_img)


if __name__ == "__main__":
    main()
