"""CPU-only structural tests: 720 scenario keys and frozen-192 regression.

These tests use deterministic fabricated objective values solely for structural QA;
they do NOT constitute physical/model results, and never enter the manuscript.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_all_weather_year_720lp import (
    WEATHER_YEARS,PILOT_YEARS,CASE_KEYS,EXPECTED,
    summarize_all,check_frozen_192,
)
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    STATES,DESIGNS,DURATIONS,
)
from energy_transition.reeds2022_96lp_hour_approximation_192lp import MODES


def fake_panel():
    rows=[]
    for y in WEATHER_YEARS:
        for st in STATES:
            for scheme in DESIGNS:
                for mode in MODES:
                    for h in DURATIONS:
                        rows.append(dict(weather_year=y,state=st,county_weight_scheme=scheme,
                            hour_approximation=mode,battery_duration_h=h,
                            objective_illustrative_variable_usd=1000000.-1000.*h+
                                (1 if scheme==DESIGNS[1] else 0)*h*10,
                            storage_capacity_mwh=float(h*100 if h else 0),
                            solver_status="optimal",max_equality_residual_mwh=1e-12))
    return pd.DataFrame(rows)


def test_complete_year_set_and_720_structural_pairs():
    assert WEATHER_YEARS==tuple(list(range(2007,2014))+list(range(2016,2024)))
    assert 2014 not in WEATHER_YEARS and 2015 not in WEATHER_YEARS
    full=fake_panel()
    assert len(full)==EXPECTED==720
    duration,geo,pairs=summarize_all(full)
    assert (len(duration),len(geo),len(pairs))==(240,120,60)
    assert pairs.same_sign.all()


def test_fail_closed_missing_or_duplicate_case():
    frame=fake_panel()
    with pytest.raises(ValueError,match="720 unique"):
        summarize_all(frame.iloc[:-1])
    bad=frame.copy()
    bad.loc[0,CASE_KEYS]=bad.loc[1,CASE_KEYS].to_numpy()
    with pytest.raises(ValueError,match="720 unique"):
        summarize_all(bad)


def test_frozen_regression_exact_cases_and_tolerance(tmp_path):
    full=fake_panel()
    prior=full[full.weather_year.isin(PILOT_YEARS)].copy()
    path=tmp_path/"frozen.csv"
    prior.to_csv(path,index=False)
    assert check_frozen_192(full,path)==0.
    prior.loc[prior.index[0],"objective_illustrative_variable_usd"]+=0.2
    prior.to_csv(path,index=False)
    with pytest.raises(ValueError,match="anchor drift"):
        check_frozen_192(full,path)
