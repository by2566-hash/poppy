"""
"Is my street dangerous?" - NYC MV crash data (h9gi-nx95), 2012-07-01..2026-06-11.

The question as asked is not answerable as stated. This script establishes why,
quantifies the constraints, and builds the framework to answer it once the
street + travel mode are specified.
"""
import duckdb
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option("display.width", 200)
con = duckdb.connect()
SRC = "'data/crashes.parquet'"

# ---------------------------------------------------------------- 1. coverage
cover = con.sql(f"""
    SELECT count(*)                        AS crashes,
           min(crash_date)                 AS first_date,
           max(crash_date)                 AS last_date,
           count(DISTINCT on_street_name)  AS street_names,
           sum(number_of_persons_killed)   AS killed,
           sum(number_of_persons_injured)  AS injured
    FROM {SRC}
""").df()

# ------------------------------------------------- 2. street names are ambiguous
# A street NAME does not identify a street: the same name recurs across boroughs.
ambig = con.sql(f"""
    WITH t AS (
        SELECT trim(upper(on_street_name)) AS street, borough
        FROM {SRC}
        WHERE trim(coalesce(on_street_name,'')) <> ''
    )
    SELECT count(*) AS names, sum(nb) AS names_in_2plus_boroughs
    FROM (SELECT street, count(DISTINCT borough) AS nb FROM t GROUP BY 1)
""").df().iloc[0]

# BROADWAY as the cleanest illustration: one name, five genuinely different roads
broadway = con.sql(f"""
    SELECT borough, count(*) AS crashes,
           sum(number_of_persons_killed)  AS killed,
           sum(number_of_persons_injured) AS injured,
           sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS ped,
           sum(number_of_cyclist_injured    + number_of_cyclist_killed)    AS cyc
    FROM {SRC}
    WHERE trim(upper(coalesce(on_street_name,''))) = 'BROADWAY'
      AND borough IS NOT NULL
    GROUP BY 1 ORDER BY crashes DESC
""").df()

# ------------------------------------------- 3. what the dataset actually counts
# Police report required for injury, death, or >= $1,000 damage. Minor
# fender-benders are absent, so this counts SEVERE events, not all events.
severity_mix = con.sql(f"""
    SELECT year(crash_date) AS yr,
           count(*) AS crashes,
           100.0 * count(*) FILTER (WHERE number_of_persons_injured > 0
                                      OR number_of_persons_killed > 0) / count(*) AS pct_injury,
           1000.0 * sum(number_of_persons_killed) / count(*) AS killed_per_1k
    FROM {SRC} GROUP BY 1 ORDER BY 1
""").df()

# ------------------------------------------------- 4. mode changes the verdict
by_mode = con.sql(f"""
    SELECT borough, count(*) AS crashes,
      1000.0 * sum(number_of_pedestrians_injured + number_of_pedestrians_killed) / count(*) AS peds_1k,
      1000.0 * sum(number_of_cyclist_injured    + number_of_cyclist_killed)    / count(*) AS cyc_1k,
      1000.0 * sum(number_of_motorist_injured    + number_of_motorist_killed)    / count(*) AS mot_1k
    FROM {SRC} WHERE borough IS NOT NULL GROUP BY 1 ORDER BY crashes DESC
""").df()

# ------------------------------------- 5. the metric you pick changes the rank
# Same street set, four defensible "danger" definitions.
streets = con.sql(f"""
    WITH t AS (
        SELECT trim(upper(on_street_name)) AS street, borough,
               number_of_persons_killed  AS killed,
               number_of_persons_injured AS injured,
               number_of_pedestrians_killed + number_of_pedestrians_injured AS ped,
               number_of_cyclist_killed    + number_of_cyclist_injured    AS cyc
        FROM {SRC}
        WHERE trim(coalesce(on_street_name,'')) <> '' AND borough IS NOT NULL
    )
    SELECT street, borough, count(*) AS crashes,
           sum(killed) AS killed, sum(injured) AS injured, sum(ped) AS ped, sum(cyc) AS cyc
    FROM t GROUP BY 1,2 HAVING count(*) >= 300
""").df()

streets["killed_1k"] = streets.killed / streets.crashes * 1000
streets["ped_share"] = streets.ped / streets.crashes * 1000
streets["cyc_share"] = streets.cyc / streets.crashes * 1000


def top20(df, col):
    t = df.nlargest(20, col)
    return list(zip(t.street, t.borough))


ranks = {
    "raw crash count":  top20(streets, "crashes"),
    "people killed":    top20(streets, "killed_1k"),
    "pedestrians hurt": top20(streets, "ped_share"),
    "cyclists hurt":    top20(streets, "cyc_share"),
}

# ---------------------------------------------------------------- 6. charts
plt.rcParams.update({"font.size": 9, "axes.titlesize": 11, "axes.titleweight": "bold"})

# Chart 1 - "BROADWAY" is five different roads
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
b = broadway.set_index("borough")
axes[0].bar(b.index, b.crashes, color="#4a6fa5")
axes[0].set_title('One street name, five different roads:\n"BROADWAY" crashes by borough')
axes[0].set_ylabel("police-reported crashes, 2012-2026")
axes[0].tick_params(axis="x", rotation=20)
for i, v in enumerate(b.crashes):
    axes[0].text(i, v + 120, f"{v:,}", ha="center", fontsize=8)

w = 0.27
x = list(range(len(b)))
axes[1].bar([i - w for i in x], b.ped / b.crashes * 1000, w, label="pedestrians", color="#c1574f")
axes[1].bar(list(x), b.cyc / b.crashes * 1000, w, label="cyclists", color="#e0a458")
axes[1].bar([i + w for i in x], (b.ped + b.cyc) / b.crashes * 1000, w, label="motorists", color="#7d9a6f")
axes[1].set_xticks(x)
axes[1].set_xticklabels(b.index, rotation=20)
axes[1].set_title("...and they carry different risk\n(people hurt per 1,000 crashes)")
axes[1].set_ylabel("per 1,000 crashes")
axes[1].legend(fontsize=8, frameon=False)
fig.suptitle("NYC crashes: why 'my street' is not yet a well-defined question",
             fontsize=12, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig("out/01_street_name_ambiguity.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Chart 2 - the threshold + traffic confound
fig, ax1 = plt.subplots(figsize=(11, 4.4))
s = severity_mix
ax1.bar(s.yr, s.crashes / 1000, color="#d8dee6", label="crash volume (thousands)")
ax1.set_ylabel("police-reported crashes (thousands)", color="#5a6672")
ax1.set_xlabel("year")
ax2 = ax1.twinx()
ax2.plot(s.yr, s.pct_injury, color="#c1574f", marker="o", lw=2,
         label="share involving injury/death")
ax2.set_ylabel("% of reported crashes involving injury or death", color="#c1574f")
ax2.set_ylim(0, 60)
ax2.axvspan(2019.5, 2021.5, color="#f0d9a0", alpha=.45)
ax2.text(2020.5, 55, "COVID: traffic\ncollapses", ha="center", fontsize=8, color="#8a6d1f")
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, fontsize=8, frameon=False, loc="upper left")
ax1.set_title("Only severe crashes get recorded - and 'severe' is not constant over time")
fig.tight_layout()
fig.savefig("out/02_what_the_data_counts.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Chart 3 - metric choice reorders the danger ranking
fig, ax = plt.subplots(figsize=(11, 5))
labels = list(ranks.keys())
base = [f"{a} / {b_}" for a, b_ in ranks["raw crash count"]]
M = np.array([[1 if v in ranks[l] else 0 for v in base] for l in labels])
ax.imshow(M, cmap="Greys", vmin=0, vmax=1.6, aspect="auto")
ax.set_xticks(range(len(base)))
ax.set_xticklabels([s.replace(" / ", "\n") for s in base], rotation=90, fontsize=6.5)
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=8)
ax.set_xticks(np.arange(-.5, len(base), 1), minor=True)
ax.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
ax.grid(which="minor", color="white", lw=1)
ax.tick_params(which="minor", length=0)
ax.set_title("Top-20 most dangerous streets - 4 defensible definitions, 4 different answers\n"
             "(dark = street appears on that list; n>=300 crashes)", fontsize=11)
fig.tight_layout()
fig.savefig("out/03_metric_choice_changes_rank.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 7. report
print("=== COVERAGE ===")
print(cover.to_string(index=False))
print("\n=== STREET NAMES ARE AMBIGUOUS ===")
print(f"{ambig['names']:,} distinct street names; {ambig['names_in_2plus_boroughs']:,} "
      f"({100*ambig['names_in_2plus_boroughs']/ambig['names']:.0f}%) occur in 2+ boroughs")
print("\n=== 'BROADWAY' BY BOROUGH ===")
print(broadway.to_string(index=False))
print("\n=== SEVERITY MIX OVER TIME ===")
print(severity_mix.round(2).to_string(index=False))
print("\n=== MODE-SPECIFIC RISK (per 1,000 crashes) ===")
print(by_mode.round(1).to_string(index=False))
overlap = set(ranks["raw crash count"]) & set(ranks["people killed"]) \
    & set(ranks["pedestrians hurt"]) & set(ranks["cyclists hurt"])
print("\n=== STREETS APPEARING ON ALL FOUR LISTS ===", len(overlap), "of 20")
print("\n=== TOP 15 BY PEDESTRIAN RISK ===")
print(streets.nlargest(15, "ped_share")[["street", "borough", "crashes", "ped_share", "cyc_share"]]
      .round(1).to_string(index=False))
print("\ncharts -> out/01_street_name_ambiguity.png, out/02_what_the_data_counts.png, "
      "out/03_metric_choice_changes_rank.png")