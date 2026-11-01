import csv
import pytest
from energy_transition.efs_western_partial_share_audit import audit


def make_weights(path,rows):
    with path.open("w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["state","reeds_zone","weight"])
        writer.writerows(rows)


def test_partial_western_fraction_allowed(tmp_path):
    p=tmp_path/"weights.csv"
    make_weights(p,[["NM","p31",0.4],["CA","p8",0.6],["CA","p9",0.4]])
    r=audit(p,{"NM","CA"})
    assert r["state_western_allocation_fraction"]["NM"]==0.4
    assert r["external_empirical_weights_verified"] is False


def test_over_one_rejected(tmp_path):
    p=tmp_path/"weights.csv"
    make_weights(p,[["NM","p31",0.8],["NM","p32",0.6]])
    with pytest.raises(ValueError,match="excess mass"):
        audit(p,{"NM"})


def test_missing_state_rejected(tmp_path):
    p=tmp_path/"weights.csv"
    make_weights(p,[["CA","p8",1]])
    with pytest.raises(ValueError,match="Missing source states"):
        audit(p,{"CA","NM"})
