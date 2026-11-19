"""Paper S source-derived ATB full 3x3 screening contract."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_atb_full_3x3_screen import screen
from energy_transition.paper_s_siting_design_grid_3x3_2880lp import (
    WEATHER_YEARS, STATES, DESIGNS, RATIOS, WIND_SHARES,
)

def test_full_grid_rejects_missing_rows():
    with pytest.raises(ValueError):
        screen(pd.DataFrame(), pd.DataFrame())

def test_full_grid_screen_shape_and_baseline_zero():
    from pathlib import Path
    atb = pd.read_csv(Path("data/paper_s_atb2025_v2_2030_bess_4h_8h_source_cells.csv"))
    rows = []
    for year in WEATHER_YEARS:
        for state in STATES:
            for scheme in DESIGNS:
                for ratio in RATIOS:
                    for share in WIND_SHARES:
                        v = 12.0 if (ratio == 1.5 and share == .5) else 25.0
                        rows.append({"weather_year": year, "state": state,
                            "county_weight_scheme": scheme,
                            "renewable_peak_ratio": ratio, "wind_share_ac": share,
                            "added_storage_kwh": 1000.0,
                            "marginal_4to8_usd_added_kwh_year": v})
    costs, cases, detail, overall = screen(atb, pd.DataFrame(rows))
    assert (len(costs),len(cases),len(detail),len(overall)) == (18,19440,1296,18)
    assert overall.meeting_hurdle.sum() > 0
    assert cases.loc[(cases.renewable_peak_ratio==1.5)&(cases.wind_share_ac==.5),"meets_hurdle"].sum()==0

def test_duplicate_frozen_source_case_fails():
    from pathlib import Path
    atb=pd.read_csv(Path("data/paper_s_atb2025_v2_2030_bess_4h_8h_source_cells.csv"))
    bad=pd.DataFrame([{"weather_year": 2012, "state":"CO",
      "county_weight_scheme":"potential", "renewable_peak_ratio":2.0,
      "wind_share_ac":.5, "added_storage_kwh":1000.0,
      "marginal_4to8_usd_added_kwh_year":20.0}]*1080)
    with pytest.raises(ValueError):
        screen(atb,bad)
