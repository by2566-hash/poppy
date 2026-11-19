import csv

import duckdb
import matplotlib.pyplot as plt
import numpy as np


con = duckdb.connect()
rows = con.execute(
    """SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
              SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
              SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
       FROM read_parquet('./data/crashes.parquet')
       WHERE crash_date >= DATE '2013-01-01'
         AND crash_date < DATE '2026-01-01'
       GROUP BY year
       ORDER BY year"""
).fetchall()
years = [row[0] for row in rows]
motorists = [row[1] for row in rows]
cyclists = [row[2] for row in rows]
differences = [m - c for m, c in zip(motorists, cyclists)]

with open('./out/values_1.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['year', 'road_user_group', 'recorded_deaths'])
    for year, motorist, cyclist in rows:
        writer.writerow([year, 'Motorist', motorist])
        writer.writerow([year, 'Cyclist', cyclist])

with open('./out/values_2.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['year', 'motorist_deaths', 'cyclist_deaths', 'motorist_minus_cyclist_deaths'])
    writer.writerows(rows[i] + (differences[i],) for i in range(len(rows)))

plt.rcParams.update({'font.size': 10, 'axes.titlesize': 14})
fig, ax = plt.subplots(figsize=(13, 6.7))
x = np.arange(len(years))
width = 0.38
ax.bar(x - width / 2, motorists, width, label='Motorist', color='#31688e')
ax.bar(x + width / 2, cyclists, width, label='Cyclist', color='#f28e2b')
ax.set_xticks(x, years)
ax.set_ylabel('Recorded deaths (count)')
ax.set_xlabel('Calendar year')
fig.suptitle('Annual recorded motorist and cyclist deaths\nNYC police-reported motor vehicle crashes, 2013–2025',
             y=0.98, fontsize=14)
fig.text(0.5, 0.91,
         'Counts are deaths recorded on crash reports; not independent death-registry totals or exposure-adjusted rates.',
         ha='center', va='center', fontsize=9, color='#444444')
ax.legend(frameon=False, ncol=2, loc='upper right')
ax.grid(axis='y', alpha=0.2)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(rect=[0, 0, 1, 0.87])
fig.savefig('./out/option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

fig, ax = plt.subplots(figsize=(12.5, 6.5))
colors = ['#31688e' if value >= 0 else '#f28e2b' for value in differences]
ax.bar(years, differences, color=colors, width=0.72)
ax.axhline(0, color='#333333', linewidth=1)
ax.set_xticks(years)
ax.set_ylabel('Motorist deaths minus cyclist deaths (count)')
ax.set_xlabel('Calendar year')
fig.suptitle('Annual difference in recorded deaths: motorist minus cyclist\nNYC police-reported motor vehicle crashes, 2013–2025',
             y=0.98, fontsize=14)
fig.text(0.5, 0.91,
         'Positive means more recorded motorist deaths; negative means more cyclist deaths. Counts are not independently audited or exposure-adjusted.',
         ha='center', va='center', fontsize=9, color='#444444')
ax.grid(axis='y', alpha=0.2)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(rect=[0, 0, 1, 0.87])
fig.savefig('./out/option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)
