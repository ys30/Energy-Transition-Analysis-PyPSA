from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from energy_transition.efs_zonal_archive_hourly_equivalence import compare


def fixture():
    nets = {}
    rows = []
    for year in (2030, 2040, 2050):
        loads = {}
        for zone, state, value in [("p1", "Arizona", 10.), ("p2", "New Mexico", 0.)]:
            key = f"EFS_{year}_{zone}_{state}"
            loads[key] = (zone, state, value)
            for hour in range(1, 8761):
                rows.append({"year": year, "state": state, "reeds_zone": zone,
                             "local_hour_id": hour, "allocated_mw": value})
        n = SimpleNamespace()
        n.snapshots = pd.date_range(f"{year}-01-01", periods=8760, freq="h")
        n.loads = pd.DataFrame({"p_set": [10., 0.]}, index=list(loads))
        n.loads_t = SimpleNamespace(p_set=pd.DataFrame(
            {f"EFS_{year}_p1_Arizona": np.full(8760, 10.)}))
        nets[year] = n
    return nets, pd.DataFrame(rows)


def test_exact_hourly_three_year_match():
    nets, rows = fixture()
    report = compare(nets, rows)
    assert all(x["hourly_mw_mismatches"] == 0 for x in report["year_results"])
    assert all(x["hourly_load_values_compared"] == 17520 for x in report["year_results"])
    assert report["cross_state_synchronous_UTC_verified"] is False


def test_reject_single_hour_corruption():
    nets, rows = fixture()
    rows.loc[0, "allocated_mw"] = 11.
    with pytest.raises(ValueError, match="hourly MW mismatches"):
        compare(nets, rows)


def test_reject_duplicate_source_hour():
    nets, rows = fixture()
    rows = pd.concat([rows, rows.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate"):
        compare(nets, rows)
