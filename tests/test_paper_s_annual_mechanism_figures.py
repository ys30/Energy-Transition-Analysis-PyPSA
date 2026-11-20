"""Gate publication figures on authentic full 15-year paired evidence."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_annual_mechanism_figures import validate

def fixtures():
    records=[]
    summary=[]
    for state,ratio in (("AZ",1.5),("CO",2.),("ID",1.5),("WY",1.5)):
        for year in (2007,2008,2009,2010,2011,2012,2013,2016,2017,2018,2019,2020,2021,2022,2023):
            base=(year-2000)*.1
            records.append({"state":state,"renewable_peak_ratio":ratio,
                "weather_year":year,"lp_spatial_effect_usd_kwh_year":base,
                "daily_spatial_effect_mwh":base*100,
                "weekly_spatial_effect_mwh":base*50,
                "annual_spatial_effect_mwh":base*200})
        summary.append({"state":state,"n_matched_weather_years":15,
            "daily_pearson_spatial_effect":1.,
            "weekly_pearson_spatial_effect":1.,
            "annual_pearson_spatial_effect":1.})
    return pd.DataFrame(records),pd.DataFrame(summary)

def test_valid_complete_15_year_figure_population():
    pairs,summary=fixtures()
    assert validate(pairs,summary)

def test_reject_missing_and_mismatched_frozen_lp():
    pairs,summary=fixtures()
    with pytest.raises(ValueError):
        validate(pairs.iloc[:-1],summary)
    altered=summary.copy()
    altered.loc[0,"annual_pearson_spatial_effect"]=-.8
    with pytest.raises(ValueError):
        validate(pairs,altered)

def test_figures_render_all_source_groups(tmp_path):
    pytest.importorskip("matplotlib")
    from energy_transition.paper_s_annual_mechanism_figures import render
    pairs,summary=fixtures()
    result=render(pairs,summary,tmp_path)
    assert result["weather_years_per_state"]==15
    for f in ("paper_s_annual_input_only_mechanism_heatmap.pdf",
              "paper_s_annual_input_only_vs_lp_scatter.png"):
        assert (tmp_path/f).stat().st_size>100
