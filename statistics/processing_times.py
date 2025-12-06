from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "airports_with_stocks.csv"
IMG_DIR = Path(__file__).resolve().parent / "imgs"
SUMMARY_CSV = Path(__file__).resolve().parent / "processing_times_summary.csv"


COLUMN_MAP = {
    "first_processing_time": "First",
    "business_processing_time": "Business",
    "premium_economy_processing_time": "PremiumEconomy",
    "economy_processing_time": "Economy",
}


def load_processing_times() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, sep=";")
    return df[list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.agg(["min", "max", "mean", "median", "std"]).T
    summary = summary.reset_index().rename(columns={"index": "class"})
    summary.to_csv(SUMMARY_CSV, index=False)
    return summary


def plot(df: pd.DataFrame) -> Path:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()
    for ax, column in zip(axes, df.columns):
        ax.hist(df[column], bins=20, color="#4C72B0", edgecolor="white", alpha=0.85)
        ax.set_title(f"{column} processing time (hours)")
        ax.set_xlabel("Hours")
        ax.set_ylabel("Count")
        ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    out_path = IMG_DIR / "processing_times.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def main() -> None:
    df = load_processing_times()
    summary = summarize(df)
    img_path = plot(df)
    print("Saved summary to", SUMMARY_CSV)
    print(summary)
    print("Saved histogram to", img_path)


if __name__ == "__main__":
    main()
