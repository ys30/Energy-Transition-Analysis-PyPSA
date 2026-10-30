# Verified 2024 BPAT wind plant identity enrichment

Evidence: successful [GitHub Actions #41087554844](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41087554844) artifact `bpat-wind-official-plant-metadata-2024`, containing `bpat_wind_official_plant_metadata_2024.csv` and `metadata_provenance.json`.

Official 2024 EIA-860 **2___Plant** workbook plant IDs were joined one-to-one to the 28 previously verified BPAT WND EIA-923 qualified plant IDs. **28/28 metadata identities matched, zero unmatched.** The output preserves qualified EIA-923 annual MWh and adds EIA-860 plant name, operator, state, county, reported BA code, latitude and longitude.

| Plant ID | Official EIA-860 plant name | State | Operator | Qualified EIA-923 2024 net MWh |
|---|---|---|---|---:|
| 57195 | Lower Snake River Wind Energy Project | WA | Puget Sound Energy Inc | 864,875 |
| 57159 | Windy Flats Wind Project | WA | Windy Flats Partners LLC | 671,560 |
| 57549 | South Hurlburt Wind LLC | OR | Caithness Shepherds Flat LLC | 619,466.82 |
| 57526 | North Hurlburt Wind LLC | OR | Caithness Shepherds Flat LLC | 619,333.48 |
| 62745 | Wheatridge Hybrid | OR | Wheatridge Wind Holdings, LLC | 616,871 |
| 57550 | Horseshoe Bend Wind LLC | OR | Caithness Shepherds Flat LLC | 608,562.11 |

## Accounting-boundary interpretation

The EIA describes its [EIA-930 reporting framework](https://www.eia.gov/electricity/930-content/about.html) as hourly balancing-authority operational reporting, with source-specific quality and corrections. [EIA-860 annual plant data](https://www.eia.gov/electricity/data/eia860/) are plant and generator survey information, including operator and reported balancing authority, not an observed hour-by-hour meter attribution.

Some BPAT-labeled EIA-860 plants have operators that are not Bonneville Power Administration; this is *not* proof of a BA assignment error. The EIA-923 BPAT wind qualified total of 8,820,435.410 MWh versus the EIA-930 hourly BPAT WND sum of 6,839,734 MWh remains a 1,980,701.410 MWh **unreconciled difference**. A fully matched plant name/ID list cannot attribute this gap to curtailment, trading, metering or any particular facility.

**Next evidence required:** documented EIA-930 BPAT WND meter reporting population or utility/BA asset treatment; plant-level hourly data that link to EIA-923 plant IDs; and an accounting boundary crosswalk. Do not rescale the EIA-930 hourly wind time series or add the 1.981-TWh difference to imports.
