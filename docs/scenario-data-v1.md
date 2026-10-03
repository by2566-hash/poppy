# Scenario and data — v1 proposal

- **Date:** 2026-10-03. **Status:** proposal for the team meeting on 2026-10-05.
- **Recommendation:** NYC traffic safety, seen through a **data journalist / fact-checker** persona, on a 3-table MVP bundle. Chicago is the transfer test; FARS is the phase-2 Honda/Ohio layer.
- Evidence: scenario deep-dive (2026-10-03, scripts kept in the research scratchpad) and E001 (`experiments/E001-data-card/`), with independent re-checks noted below.

## 1. Persona

| | P1 Data journalist / fact-checker (**MVP**) | P3 Honda / 99P vulnerable-road-user researcher (phase 2) |
|---|---|---|
| Decides | Whether a DOT, Council or advocacy claim holds; which chart and caveat to publish | Which pre-crash scenarios ADAS / V2X work should prioritize |
| Typical vague questions | "Are cyclists safer in NYC?" · "Are e-bikes making streets more dangerous?" · "Is Vision Zero failing?" | "When and where are pedestrians most at risk?" · "Are bigger vehicles deadlier to pedestrians?" |
| Why | Questions are claim-driven; competing interpretations are already argued in public (sources below); no geospatial joins or text parsing needed | Direct Honda link (zero-fatality goal), but needs Vehicles, registrations and FARS |

Real public examples of the vague questions (verified URLs in the deep-dive): NYC DOT "traffic deaths reach all-time low" (2026-01-02; 205 deaths vs 229 in open data), Transportation Alternatives "deadliest first six months" (2024-07-23), Streetsblog "Vision Zero ten years of mixed results" (2024-02-06), NYC Comptroller on micromobility (2024-10-29; its e-bike jump is mostly a categorization change), Streetsblog / Gothamist on congestion pricing and crashes (2025), NYC Council e-bike bills (2026-09-30).

## 2. Data bundle (MVP)

| Table | Source | Rows | Size | Fetch |
|---|---|---|---|---|
| `crashes` | NYC `h9gi-nx95`, 2012-07-01 → 2026-06-11 | 2,269,187 | 476 MB CSV, 61 MB Parquet (already built in E001) | done |
| `persons` (injured/killed only) | NYC `f55k-p6yu`, filtered | 759,708 | ~150 MB CSV | 1 curl (SoQL filter) |
| `bike_monthly` (exposure) | NYC `ct66-47at`, 5 East River bridge sensors, aggregated server-side | 638 | tiny | 1 curl (SoQL group) |

- **Analysis window:** full years 2013–2025. Keep 2012 and 2026 rows as trap test cases, not as data.
- **DE effort:** crashes table took 7 s of compute and 12 min of agent time (E001). Whole bundle estimated at 4–6 hours.
- **Data status:** the city froze updates at 2026-06-15; the promised August fix has not landed. Pin this snapshot. Demos must say "snapshot", never "live".

## 3. Trap catalog (unified IDs; ground truth for L3)

✔ = re-checked independently on our snapshot. S = documented by a cited source. Others come from the deep-dive and still need a re-check.

| ID | Trap | Evidence | Breaks |
|---|---|---|---|
| TR01 ✔S | NYPD stopped recording most property-damage-only crashes (Staten Island pilot Mar 2019, citywide 2020-04-06) | PDO 166,047 → 79,556 → 48,126 (2019 / 2020 / 2025) while injury crashes 45,439 → 33,362 → 37,420 | "Are crashes going down?" |
| TR02 | COVID 2020 shock, entangled with TR01 | crashes −47% in 2020 while cyclist injuries +12% | "Did safety improve in 2020?" |
| TR03 ✔ | E-bike / e-scooter riders injured since 2021 are in `persons_injured` but in none of the pedestrian / cyclist / motorist columns | hidden residual 0 (2020), 2,132 (2021), 2,411 (2023), 1,405 (2025) | "Are cyclists safer?" |
| TR04 ✔ | Vehicle-type taxonomy drift | e-bike crashes 23 (2018) → 2,688 (2021) → 1,411 (2025) while moped 193 → 693 → 1,859; scooter 1,725 → 591 (2024 → 2025); "PASSENGER VEHICLE" → "Sedan" (2016); 4-character codes from May 2026 | "Are e-bikes / SUVs getting more dangerous?" |
| TR05 ✔ | Missing location | borough null 30.47% (peak 38.1% in 2017); latitude null 10.61%; missing coordinates stored as 0 since about Nov 2024 | "Which borough is worst?", maps |
| TR06 ✔ | Cause recorded as "Unspecified" | 33.34% overall; 58.5% (2013) → 21.5% (2017) → 25.7% (2025) | "What causes crashes?" |
| TR07 S | Open-data deaths ≠ official counts | 2025: 229 in open data vs 205 per NYC DOT; 2024: 268 vs 253 | "How many people died?" |
| TR08 ✔ | Broken tail of the frozen data | killed count NULL in 87.8% of May-2026 and 100% of June-2026 rows; injured count intact | "Is 2026 worse?" |
| TR09 ✔ | Partial years | 2012 starts Jul 1; 2026 ends Jun 11 | any year-over-year at the edges |
| TR10 | Person table before Apr 2016 is a sparse backfill | sex, safety equipment, complaint 97–99% null | "Has helmet use changed?" |
| TR11 S | Counts instead of rates | East River bridge bike crossings +58% vs cyclist injuries +7% (2019 → 2025) | "Are cyclists safer?" |
| TR12 | No KABCO severity; injury labels renamed in 2018 | 62% "Complaint of Pain"; 4.9% serious categories | "Are serious injuries rising?" |
| TR13 | Time heaping | 00:00 in 1.3–2.1% of crashes since 2016 vs 0.01% before | "When is it most dangerous?" |
| TR14 | Street names padded with spaces until 2021 | ~100% padded 2012–20 | street-level questions |
| TR15 | Small-number swings | cyclist deaths 10 (2018) → 31 (2019) | "Did cyclist deaths triple?" |
| TR16 | Wrong join key (phase 2) | `person.vehicle_id` = `vehicles.unique_id`, not `vehicles.vehicle_id` | vehicle-level questions |
| TR17 | Suspected reporting-system switch, Mar 2016 (unverified) | injuries per crash 0.244 → 0.282 (Sep 2015 → Sep 2016) | "Did injuries jump in 2016?" |

Corrections to earlier claims: Person / Vehicles rows start 2012-07-01 (sparse before Apr 2016), not Apr 2016. E001's "one e-bike spelling misses 59%" mixed categories; for e-bikes alone the exact spelling covers 97%.

## 4. Alternatives considered

| Candidate | Verdict |
|---|---|
| Chicago (3 tables, daily updates, decoded labels, KABCO severity) | Best **transfer test**: run the same agent on a second city in phase 2. 5–8 DE hours, ~2.3 GB. Citywide only from Sep 2017. |
| FARS 2015–2024 (national fatal crashes; decoded NAME columns; VIN decode with make and ADAS fields) | **Phase 2** for Honda and Ohio questions (Ohio = STATE 39). 6–10 DE hours; schema drift is mechanical (`union_by_name`). |
| Ohio statewide / Columbus | **Not practical.** ODPS needs a CAPTCHA + emailed link and keeps only 5 years; ODOT tools need login; Columbus layer is static 2018–2022 with no person or mode data. Tell Ryan plainly. |
| Montgomery County, MD | Clean but small and not relatable. Not better. |

## 5. Explicitly out of MVP

Geospatial joins (congestion zone, community districts), Citi Bike trip files (31 GB), NYC Vehicles table, registrations, Census population, Chicago, FARS.
