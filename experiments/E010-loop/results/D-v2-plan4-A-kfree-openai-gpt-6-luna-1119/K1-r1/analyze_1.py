import csv

import duckdb
import matplotlib.pyplot as plt


con = duckdb.connect()
rows = con.execute(
    """
    SELECT
        year(crash_date) AS calendar_year,
        sum(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet('./data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY calendar_year
    ORDER BY calendar_year
    """
).fetchall()
con.close()

with open('./out/values_1.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['calendar_year', 'pedestrians_killed'])
    writer.writerows(rows)

years = [row[0] for row in rows]
counts = [row[1] for row in rows]

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.bar(years, counts, color='#286b8e', width=0.75)
ax.bar_label(bars, labels=[f'{value:,}' for value in counts], padding=3, fontsize=8)
ax.set_title('Pedestrians killed per year in police-reported NYC motor vehicle crashes\n(2013–2025)', pad=30, fontsize=14)
ax.text(
    0.5,
    1.015,
    'Counts are deaths recorded in crash reports; all requested calendar years are represented.',
    transform=ax.transAxes,
    ha='center',
    va='bottom',
    fontsize=9,
    color='#444444',
)
ax.set_xlabel('Calendar year of crash_date')
ax.set_ylabel('Pedestrians killed (annual count)')
ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45, ha='right')
ax.set_ylim(0, max(counts) * 1.15)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
fig.savefig('./out/option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)
