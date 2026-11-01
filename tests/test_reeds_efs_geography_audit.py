import csv
from energy_transition.reeds_efs_geography_audit import audit_membership


def test_split_state_and_missing_western_state(tmp_path):
    path = tmp_path / "membership.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ba", "st", "interconnect", "st_interconnect"])
        w.writerow(["p1", "CA", "western", "CA"])
        w.writerow(["p2", "NM", "western", "NM_western"])
        w.writerow(["p3", "NM", "eastern", "NM_eastern"])
        w.writerow(["p4", "SD", "western", "SD_western"])
    result = audit_membership(path)
    assert result["states_split_across_interconnects"] == ["NM"]
    assert result["western_states_missing_from_core_efs_pilot"] == ["SD"]
    assert result["all_state_efs_load_to_western_allowed"] is False
