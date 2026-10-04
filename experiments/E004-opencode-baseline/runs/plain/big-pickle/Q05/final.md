I'll start by reading the dataset documentation.

Data quality findings are significant. Let me build the analysis.

I left some scratch code in there. Let me clean it up.

Let me just rewrite the file cleanly.

I can't view images directly. Let me verify the charts programmatically.

Let me add a reusable street-profile function so I can answer instantly once they name their street.

`params` must be a keyword argument.

I can't answer that as asked — and the data can't either, for three specific reasons. Here's what I found, then one question.

## The dataset doesn't count "dangerous"

It only records crashes police-reported for injury, death, or ≥$1,000 damage. Minor fender-benders are invisible. Across 2012–19, ~80% of rows are damage-only — so this measures **severe events**, not all events. Worse, the mix isn't stable: the injury share jumps from 21% (2019) to 44% (2024) while volume halves, so comparing your street across years is confounded by COVID traffic collapse (`out/02_what_the_data_counts.png`).

## "My street" isn't a well-defined thing here

**91% of street names occur in 2+ boroughs** (13,305 of 14,668). "Broadway" is five different roads — Manhattan records 8,645 crashes and 756 pedestrians hurt; the Bronx, 1,055 and 76. Also: 30% of rows have no borough and 22% have no street name at all.

## The metric you pick decides the answer

Four defensible definitions of "dangerous" produce four disjoint top-20 lists — **0 streets appear on all four** (`out/03_metric_choice_changes_rank.png`). Raw volume mostly measures traffic exposure, and there's no traffic denominator to correct for it. As a demo, `street_profile.py` on Flatbush Avenue (Brooklyn):

| Metric | Percentile |
|---|---|
| crash volume | 99.8 |
| fatality rate | 70.5 |
| pedestrian harm | 41.9 |
| cyclist harm | 32.2 |

Top of the city by volume, middling for pedestrians. Your answer depends entirely on which of those you're asking about.

## So I need two things

**Which street, including borough** — and ideally a cross street, since one name spans many blocks with very different profiles (Fulton Street, Brooklyn: 225 pedestrians hurt per 1,000 crashes).

**How you use it** — walking, cycling, or driving changes the risk by 3x. Per1,000 crashes: pedestrians are hurt 75x in the Bronx vs motorists 247x in Staten Island. The street that's dangerous for you may be unremarkable for a driver.

Then run: `python3 street_profile.py "YOUR STREET" --borough BOROUGH`

Charts in `out/`: `01_street_name_ambiguity.png`, `02_what_the_data_counts.png`, `03_metric_choice_changes_rank.png`.