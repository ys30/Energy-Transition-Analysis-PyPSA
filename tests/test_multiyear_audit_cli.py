"""End-to-end CLI audit tests with synthetic CSV fixtures only."""
import numpy as np
import pandas as pd
import pytest

from energy_transition.multiyear_audit import run


def make_inputs(tmp_path, years=(2023, 2024)):
    frames = []
    for year in years:
        hours = pd.date_range(f"{year}-01-01", f"{year+1}-01-01",
                              freq="h", inclusive="left", tz="UTC")
        for state, mw in [("CA", 100.0), ("NV", 40.0)]:
            frames.append(pd.DataFrame({
                "timestamp_utc": hours, "state": state, "load_mw": mw}))
    load = pd.concat(frames, ignore_index=True)
    load_path = tmp_path / "load.csv"
    weights_path = tmp_path / "weights.csv"
    load.to_csv(load_path, index=False)
    pd.DataFrame([
        ("CA", "CA_A", 0.3), ("CA", "CA_B", 0.7),
        ("NV", "NV_A", 1.0)], columns=["state", "zone", "weight"]
    ).to_csv(weights_path, index=False)
    return load, load_path, weights_path


def test_two_year_cli_accounting_and_output(tmp_path):
    _, load, weights = make_inputs(tmp_path)
    out = tmp_path / "nested" / "audit.csv"
    report = run(load, weights, out)
    assert out.exists()
    assert len(report) == 4
    assert set(report["year"]) == {2023, 2024}
    assert set(report.loc[report.year == 2024, "hours"]) == {8784}
    assert set(report.loc[report.year == 2023, "hours"]) == {8760}
    np.testing.assert_allclose(report["difference_mwh"], 0, atol=1e-7)
    assert pd.read_csv(out).shape[0] == 4


def test_missing_hour_rejected_without_output(tmp_path):
    raw, load, weights = make_inputs(tmp_path, years=(2024,))
    raw = raw.drop(raw.index[0])
    raw.to_csv(load, index=False)
    out = tmp_path / "audit.csv"
    with pytest.raises(ValueError):
        run(load, weights, out)
    assert not out.exists()


def test_shared_zone_rejected_without_output(tmp_path):
    _, load, weights = make_inputs(tmp_path, years=(2024,))
    pd.DataFrame([
        ("CA", "shared", 1.0), ("NV", "shared", 1.0)],
        columns=["state", "zone", "weight"]).to_csv(weights, index=False)
    out = tmp_path / "audit.csv"
    with pytest.raises(ValueError, match="more than one state"):
        run(load, weights, out)
    assert not out.exists()


def test_duplicate_state_hour_rejected(tmp_path):
    raw, load, weights = make_inputs(tmp_path, years=(2024,))
    pd.concat([raw, raw.iloc[[0]]], ignore_index=True).to_csv(load, index=False)
    with pytest.raises(ValueError, match="duplicate timestamp/state"):
        run(load, weights, tmp_path / "audit.csv")


def test_missing_state_year_rejected(tmp_path):
    raw, load, weights = make_inputs(tmp_path)
    raw = raw.loc[~((raw.state == "NV") &
                    (raw.timestamp_utc.dt.year == 2023))]
    raw.to_csv(load, index=False)
    with pytest.raises(ValueError, match="incomplete state coverage"):
        run(load, weights, tmp_path / "audit.csv")


def test_strict_source_admission_with_manifest(tmp_path):
    import hashlib
    import json
    _, load, weights = make_inputs(tmp_path, years=(2024,))
    mapping = tmp_path / "mapping.json"
    manifest = tmp_path / "manifest.json"
    mapping.write_text(json.dumps({
        "state_to_all_membership_zones": {"CA": ["CA_A", "CA_B"], "NV": ["NV_A"]},
        "state_to_network_zones": {"CA": ["CA_A", "CA_B"], "NV": ["NV_A"]},
    }))
    payload = {
        "weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
        "source_url": "https://example.org/test-only",
        "source_revision": "synthetic-fixture",
        "geographic_method": "population_geographic_overlay",
        "geography_vintage": "2020",
        "population_vintage": "2020",
        "processing_script_sha256": "a" * 64,
        "coverage_note": "synthetic-only, not empirical",
    }
    manifest.write_text(json.dumps(payload))
    out = tmp_path / "audit.csv"
    assert len(run(load, weights, out, mapping_path=mapping, manifest_path=manifest)) == 2
    out.unlink()
    payload["weights_sha256"] = "b" * 64
    manifest.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="provenance"):
        run(load, weights, out, mapping_path=mapping, manifest_path=manifest)
    assert not out.exists()


def test_strict_requires_both_evidence_files(tmp_path):
    _, load, weights = make_inputs(tmp_path, years=(2024,))
    with pytest.raises(ValueError, match="provided together"):
        run(load, weights, tmp_path / "audit.csv", mapping_path="missing.json")


def test_timezone_naive_input_rejected(tmp_path):
    raw, load, weights = make_inputs(tmp_path, years=(2024,))
    raw["timestamp_utc"] = raw["timestamp_utc"].dt.strftime("%Y-%m-%d %H:%M:%S")
    raw.to_csv(load, index=False)
    with pytest.raises(ValueError, match="explicit UTC"):
        run(load, weights, tmp_path / "audit.csv")


def test_non_utc_offset_rejected(tmp_path):
    raw, load, weights = make_inputs(tmp_path, years=(2024,))
    raw["timestamp_utc"] = raw["timestamp_utc"].dt.strftime("%Y-%m-%dT%H:%M:%S-07:00")
    raw.to_csv(load, index=False)
    with pytest.raises(ValueError, match="explicit UTC"):
        run(load, weights, tmp_path / "audit.csv")


def test_negative_load_rejected(tmp_path):
    raw, load, weights = make_inputs(tmp_path, years=(2024,))
    raw.loc[0, "load_mw"] = -1.0
    raw.to_csv(load, index=False)
    with pytest.raises(ValueError, match="invalid load"):
        run(load, weights, tmp_path / "audit.csv")


def test_weight_sum_mismatch_rejected(tmp_path):
    _, load, weights = make_inputs(tmp_path, years=(2024,))
    w = pd.read_csv(weights)
    w.loc[w.zone == "CA_A", "weight"] = 0.2
    w.to_csv(weights, index=False)
    with pytest.raises(ValueError, match="do not sum to one"):
        run(load, weights, tmp_path / "audit.csv")


def test_partial_year_rejected(tmp_path):
    raw, load, weights = make_inputs(tmp_path, years=(2024,))
    raw = raw.loc[raw.timestamp_utc.dt.month <= 6]
    raw.to_csv(load, index=False)
    with pytest.raises(ValueError, match="out-of-year hours"):
        run(load, weights, tmp_path / "audit.csv")
