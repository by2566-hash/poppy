I'll start by reading the dataset documentation.

2.27M crashes, 2012–2026. Let me normalize the messy vehicle-type codes across all 5 vehicle columns.

Rich messy codes. Let me build a normalization layer and compute the core trends.

My classifier has a logic bug (e-bike slots fell through to unknown). Let me rewrite it cleanly: base category first, then split electric vs. non-electric.

Found it — my `out[electric] = "other_electric"` catch-all was overwriting the specific labels. Fixing order:

Classification now reconciles with raw counts. Setting up the analysis plan:

Found a serious bug: `groupby` sorted by `collision_id`, so my `.values` assignment scrambled rows. The `ebike_any` counts were garbage. Let me fix with a proper key-based join.

pivot_table on 11M rows was too slow. Let me vectorize with numpy positionally instead.