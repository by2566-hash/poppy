import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_counts():
    con = duckdb.connect()
    data_path = str(DATA).replace("'", "''")
    return con.execute(
        f"""SELECT strftime(crash_date, '%A') AS weekday, COUNT(*) AS crash_records
            FROM read_parquet('{data_path}')
            WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
            GROUP BY weekday"""
    ).fetchdf().set_index("weekday").reindex(WEEKDAYS).reset_index()


def chart(path, values, title, ylabel, note, percent=False):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    column = "share_percent" if percent else "crash_records"
    bars = ax.bar(values["weekday"], values[column], color="#2878B5")
    ax.set_title(title, fontsize=14, weight="bold", pad=14)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Weekday of crash date")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=20)
    if percent:
        ax.set_ylim(0, max(values[column]) * 1.17)
        labels = [f"{v:.2f}%" for v in values[column]]
    else:
        ax.set_ylim(0, max(values[column]) * 1.17)
        labels = [f"{v:,.0f}" for v in values[column]]
    ax.bar_label(bars, labels=labels, padding=3, fontsize=8)
    fig.text(0.5, 0.015, note, ha="center", va="bottom", fontsize=8, color="#444444")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    values = get_counts()
    values["crash_records"] = values["crash_records"].astype("int64")
    total = int(values["crash_records"].sum())

    values.to_csv(OUT / "values_1.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    chart(
        OUT / "option_1.png",
        values,
        "Count of NYC police-reported crash records by weekday\n2013–2025 (2,132,218 crashes)",
        "Number of crash records",
        "Limitation: record counts are not adjusted for traffic exposure and do not measure crash risk.",
    )

    shares = values.copy()
    shares["share_percent"] = shares["crash_records"] / total * 100
    shares.to_csv(OUT / "values_2.csv", index=False, float_format="%.8f")
    chart(
        OUT / "option_2.png",
        shares,
        "Share of all NYC police-reported crash records by weekday\n2013–2025 (2,132,218 crashes)",
        "Share of all crash records (%)",
        "Limitation: shares describe reported-crash composition, not traffic-adjusted crash risk.",
        percent=True,
    )


if __name__ == "__main__":
    main()
