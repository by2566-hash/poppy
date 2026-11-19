The parquet schema uses `number_of_motorist_killed` (singular), while the provided column description says `number_of_motorists_killed`. I’m using the actual field name and will document the schema mismatch in the check outputs.
ANSWER:

1. Per-mile risk cannot be determined from these records; reported motorist deaths per 1,000 police-reported crashes were 0.540 in 2013 and 0.947 in 2025 ([chart](out/option_1.png)).
2. Per-mile risk cannot be determined from these records; crashes reporting at least one motorist death were 0.050% of crash rows in 2013 and 0.088% in 2025 ([chart](out/option_2.png)).