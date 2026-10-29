import pandas as pd
import pytest

from energy_transition.eia860_ba_crosswalk import map_generators_to_bas


def fixture():
    g = pd.DataFrame({
        "plant_id": ["101", "101", "102"],
        "generator_id": ["G1", "G2", "G1"],
        "capacity_mw": [100, 50, 25],
        "fuel": ["NG", "SUN", "WND"],
        "report_year": [2024] * 3,
        "status": ["OP"] * 3,
    })
    x = pd.DataFrame({
        "plant_id": ["101", "102"],
        "balancing_authority": ["CISO", "BPAT"],
        "mapping_year": [2024, 2024],
        "source": ["verified mapping A", "verified mapping B"],
    })
    return g, x


def test_mapping_preserves_generator_capacity():
    g, x = fixture()
    grouped, unmatched, audit = map_generators_to_bas(g, x, 2024, ("CISO", "BPAT"))
    assert grouped.nameplate_mw.sum() == pytest.approx(175)
    assert len(unmatched) == 0
    assert audit["mapped_capacity_fraction"] == 1


def test_duplicate_plant_mapping_rejected():
    g, x = fixture()
    x = pd.concat([x, x.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        map_generators_to_bas(g, x, 2024, ("CISO", "BPAT"))


def test_unmapped_capacity_fails_threshold():
    g, x = fixture()
    with pytest.raises(ValueError, match="coverage"):
        map_generators_to_bas(g, x.iloc[:1], 2024, ("CISO", "BPAT"))


def test_wrong_year_rejected():
    g, x = fixture()
    x["mapping_year"] = 2023
    with pytest.raises(ValueError, match="years"):
        map_generators_to_bas(g, x, 2024, ("CISO", "BPAT"))
