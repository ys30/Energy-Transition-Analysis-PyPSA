import json

import pandas as pd
import pytest

from energy_transition.eia930_west import load_ba_capacity


def _input(tmp_path, rows, coverage=0.98):
    path = tmp_path / "ba_operating_nameplate_by_fuel_2024.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    (tmp_path / "ba_crosswalk_manifest_2024.json").write_text(
        json.dumps({"year": 2024, "operating_nameplate_mapping_fraction": coverage})
    )
    return path


def test_reject_unsupported_fuels_instead_of_silent_omission(tmp_path):
    p = _input(tmp_path, [
        {"ba_code": "CISO", "fuel": "NG", "capacity_mw": 100},
        {"ba_code": "CISO", "fuel": "WND", "capacity_mw": 20},
        {"ba_code": "CISO", "fuel": "SUN", "capacity_mw": 30},
        {"ba_code": "CISO", "fuel": "WAT", "capacity_mw": 40},
    ])
    with pytest.raises(ValueError, match="nonzero hydro"):
        load_ba_capacity(p, ["CISO"])


def test_supported_capacity_scenario(tmp_path):
    p = _input(tmp_path, [
        {"ba_code": "CISO", "fuel": "NG", "capacity_mw": 100},
        {"ba_code": "CISO", "fuel": "WND", "capacity_mw": 20},
        {"ba_code": "CISO", "fuel": "SUN", "capacity_mw": 30},
        {"ba_code": "BPAT", "fuel": "NG", "capacity_mw": 10},
    ])
    assert load_ba_capacity(p, ["CISO"]) == {"gas": 100, "wind": 20, "solar": 30}


def test_reject_insufficient_ba_mapping_coverage(tmp_path):
    p = _input(tmp_path, [
        {"ba_code": "CISO", "fuel": "NG", "capacity_mw": 100},
    ], coverage=0.9)
    with pytest.raises(ValueError, match="coverage"):
        load_ba_capacity(p, ["CISO"])


def test_capacity_vintage_must_match_requested_year(tmp_path):
    p = _input(tmp_path, [
        {"ba_code": "CISO", "fuel": "NG", "capacity_mw": 100},
        {"ba_code": "CISO", "fuel": "WND", "capacity_mw": 20},
        {"ba_code": "CISO", "fuel": "SUN", "capacity_mw": 30},
    ])
    (tmp_path / "ba_crosswalk_manifest_2024.json").write_text(
        json.dumps({"year": 2024, "operating_nameplate_mapping_fraction": 0.98})
    )
    with pytest.raises(ValueError, match="vintage mismatch"):
        load_ba_capacity(p, ["CISO"], year=2023)
    assert load_ba_capacity(p, ["CISO"], year=2024)["gas"] == 100
