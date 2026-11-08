import numpy as np
import pandas as pd
import pytest

from energy_transition.paper_s_marginal_duration_figures import validate, make_figures


def data():
    rows=[]
    for year in (2030,2040,2050):
        for shape in ("flat_50pct","ordinal24_wave_A","ordinal24_wave_B"):
            r={"planning_year":year,"synthetic_supply_shape":shape,
               "zones":20,"source_ordinal_hours_per_case":8760}
            for metric in ("unused_renewable_mwh","objective_illustrative_variable_usd"):
                v = 1e6 if metric == "unused_renewable_mwh" else 1e9
                r[f"{metric}_0h"]=100*v
                r[f"{metric}_4h"]=80*v
                r[f"{metric}_8h"]=72*v
                r[f"{metric}_reduction_0to4h"]=20*v
                r[f"{metric}_reduction_4to8h"]=8*v
            rows.append(r)
    return pd.DataFrame(rows)


def test_real_figure_outputs_and_manifest(tmp_path):
    r=make_figures(data(),tmp_path)
    assert r["year_shape_comparisons"]==9
    assert len(r["files"])==4
    assert not r["western_opf"]
    assert all((tmp_path/f).stat().st_size>1000 for f in r["files"])


def test_tampered_difference_rejected():
    d=data()
    d.loc[0,"unused_renewable_mwh_reduction_4to8h"]+=20000
    with pytest.raises(ValueError,match="4-to-8"):
        validate(d)


def test_nonfinite_rejected():
    d=data()
    d.loc[0,"objective_illustrative_variable_usd_8h"]=np.nan
    with pytest.raises(ValueError,match="Nonfinite"):
        validate(d)


def test_missing_shape_rejected():
    with pytest.raises(ValueError,match="Incomplete"):
        validate(data().iloc[:-1])
