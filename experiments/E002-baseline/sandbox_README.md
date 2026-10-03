# NYC Motor Vehicle Collisions — Crashes

Source: NYC Open Data, dataset `h9gi-nx95` ("Motor Vehicle Collisions - Crashes"), published by the NYPD. Snapshot downloaded 2026-10-03.

Official description (paraphrased): each row is one police-reported motor vehicle collision in New York City. A police report (MV-104AN) is required when someone is injured or killed, or when there is at least $1,000 of damage. The data is preliminary and subject to change.

File: `crashes.parquet` (one row per crash)

| Column | Type | Description |
|---|---|---|
| collision_id | BIGINT | Unique identifier of the crash |
| crash_date | DATE | Date of the crash |
| crash_time | TIME | Time of the crash |
| borough | VARCHAR | Borough where the crash occurred |
| zip_code | VARCHAR | Postal code of the crash location |
| latitude, longitude | DOUBLE | Coordinates of the crash location |
| location | VARCHAR | Latitude/longitude pair |
| on_street_name | VARCHAR | Street on which the crash occurred |
| cross_street_name | VARCHAR | Nearest cross street |
| off_street_name | VARCHAR | Street address if known |
| number_of_persons_injured / _killed | INTEGER | People injured / killed |
| number_of_pedestrians_injured / _killed | INTEGER | Pedestrians injured / killed |
| number_of_cyclist_injured / _killed | INTEGER | Cyclists injured / killed |
| number_of_motorist_injured / _killed | INTEGER | Vehicle occupants injured / killed |
| contributing_factor_vehicle_1 … _5 | VARCHAR | Factor contributing to the crash, for each vehicle involved |
| vehicle_type_code1 … 5 | VARCHAR | Type of each vehicle involved |
