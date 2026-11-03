import csv
import pytest
from energy_transition.efs_real_network_zone_gate import validate


def write(path, headers, rows):
    with path.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)


def test_real_zone_allowlist_and_partial_state(tmp_path):
    b=tmp_path/"bus.csv";w=tmp_path/"laf.csv"
    write(b,["state","reeds_zone","bus_count"],[["New Mexico","p31",308],["California","p8",23]])
    write(w,["state","reeds_zone","weight"],[["New Mexico","p31",0.65]])
    r=validate(b,w)
    assert r["all_laf_zones_in_real_network"]
    assert r["state_weight_sums"]["New Mexico"]==0.65
    assert not r["empirical_laf_provenance_confirmed"]


def test_reject_zone_not_in_built_network(tmp_path):
    b=tmp_path/"bus.csv";w=tmp_path/"laf.csv"
    write(b,["state","reeds_zone","bus_count"],[["Texas","p59",104]])
    write(w,["state","reeds_zone","weight"],[["Texas","p60",0.02]])
    with pytest.raises(ValueError,match="absent from real network"):
        validate(b,w)


@pytest.mark.parametrize("bad_weight", ["nan", "inf", "-0.1", "1.01", "oops", ""])
def test_reject_nonfinite_or_invalid_laf_weight(tmp_path, bad_weight):
    buses = tmp_path / "bus.csv"
    weights = tmp_path / "laf.csv"
    write(buses, ["state", "reeds_zone", "bus_count"], [["NM", "p31", 4]])
    write(weights, ["state", "reeds_zone", "weight"], [["NM", "p31", bad_weight]])
    with pytest.raises(ValueError, match="Invalid LAF share|Blank EFS LAF"):
        validate(buses, weights)


@pytest.mark.parametrize("bad_count", ["0", "-1", "nan", "1.5", ""])
def test_reject_invalid_crosswalk_bus_count(tmp_path, bad_count):
    buses = tmp_path / "bus.csv"
    weights = tmp_path / "laf.csv"
    write(buses, ["state", "reeds_zone", "bus_count"], [["NM", "p31", bad_count]])
    write(weights, ["state", "reeds_zone", "weight"], [["NM", "p31", "0.5"]])
    with pytest.raises(ValueError, match="Invalid bus_count|Blank real-network"):
        validate(buses, weights)


def test_reject_duplicate_or_conflicting_network_zones(tmp_path):
    buses = tmp_path / "bus.csv"
    weights = tmp_path / "laf.csv"
    write(weights, ["state", "reeds_zone", "weight"], [["NM", "p31", "0.5"]])
    write(buses, ["state", "reeds_zone", "bus_count"],
          [["NM", "p31", 4], ["NM", "p31", 5]])
    with pytest.raises(ValueError, match="Duplicate real-network zone"):
        validate(buses, weights)
    write(buses, ["state", "reeds_zone", "bus_count"],
          [["NM", "p31", 4], ["AZ", "p31", 5]])
    with pytest.raises(ValueError, match="multiple states"):
        validate(buses, weights)


def test_reject_duplicate_laf_zone(tmp_path):
    buses = tmp_path / "bus.csv"
    weights = tmp_path / "laf.csv"
    write(buses, ["state", "reeds_zone", "bus_count"], [["NM", "p31", 4]])
    write(weights, ["state", "reeds_zone", "weight"],
          [["NM", "p31", 0.3], ["NM", "p31", 0.3]])
    with pytest.raises(ValueError, match="Duplicate allocation zone"):
        validate(buses, weights)
