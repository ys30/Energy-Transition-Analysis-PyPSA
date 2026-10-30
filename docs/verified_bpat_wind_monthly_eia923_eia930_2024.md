# Verified BPAT 2024 wind: EIA-923 versus EIA-930 monthly reporting boundary

Evidence: [successful GitHub Actions #41086017492](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41086017492), artifact `bpat-wind-monthly-boundary-2024`, `bpat_wind_eia923_eia930_monthly_comparison.csv`.

EIA-923 monthly plant-reported BPAT wind (Page 1 sum of numeric reported plant/fuel monthly rows) and EIA-930 hourly BPAT WND signed net generation were evaluated by month for 2024. EIA-930 is expressed in **UTC calendar months**, whereas EIA-923 follows reported monthly plant accounting; they must not be assumed to have perfectly identical reporting populations or time-zone boundaries.

| Month | EIA-923 monthly wind (MWh) | EIA-930 signed hourly wind (MWh) | EIA-923 minus EIA-930 (MWh) | EIA-930 valid/expected hours |
|---|---:|---:|---:|---:|
| Jan | 500,092.00 | 388,181 | 111,911 | 744/744 |
| Feb | 630,933.00 | 481,898 | 149,035 | 696/696 |
| Mar | 661,765.00 | 520,961 | 140,804 | 744/744 |
| Apr | 982,478.00 | 766,774 | 215,704 | 720/720 |
| May | 1,164,485.00 | 927,436 | 237,049 | 744/744 |
| Jun | 886,124.00 | 675,036 | 211,088 | 720/720 |
| Jul | 779,986.00 | 613,900 | 166,086 | 744/744 |
| Aug | 767,207.00 | 590,067 | 177,140 | 744/744 |
| Sep | 732,750.41 | 565,770 | 166,980.41 | 720/720 |
| Oct | 607,001.00 | 463,910 | 143,091 | 744/744 |
| Nov | 646,599.00 | 495,721 | 150,878 | 720/720 |
| Dec | 461,015.00 | 350,080 | 110,935 | 744/744 |
| **Year** | **8,820,435.41** | **6,839,734** | **1,980,701.41** | **8,784/8,784** |

The gap is **22.46% of EIA-923 wind generation** (or 28.96% of EIA-930 wind generation). Every month shows EIA-923 greater than EIA-930; the discrepancy is not created by missing EIA-930 BPAT wind hours, because all 8,784 were observed and numeric.

**Important:** This is **not** proof of curtailed generation, transmission losses or a time-zone problem. Even all-qualified EIA-923 source records and matching EIA-860 plant BA codes do not establish an identical operational accounting population with EIA-930. EIA-923 monthly reporting versus EIA-930 hourly BA net generation may differ in data definitions, facility membership, behind-the-meter accounting, report corrections and time boundaries. Do not use the 1.981-TWh difference to adjust PyPSA interchange or annual supply.

Next step: identify the 28 matched BPAT wind plant/fuel EIA-923 source records, check source BA ownership and accounting definition plant by plant, and compare to independently documented EIA-930 reporting methodology. Retain both sources without treating one as a correction to the other.
