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
