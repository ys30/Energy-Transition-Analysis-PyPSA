"""Synthetic-only regression tests for provenance-gated zonal export."""
import numpy as np
import pandas as pd
import pytest

from energy_transition.export_zonal_loads import export_zonal_loads


def test_export_rejects_missing_provenance_by_default(tmp_path):
    with pytest.raises(ValueError, match="Production mode requires"):
        export_zonal_loads("missing.csv", "missing_weights.csv",
                           tmp_path / "audit.csv", tmp_path / "zones.csv")


def test_export_two_years_and_conserve_mwh(tmp_path):
    frames = []
    for year in (2023, 2024):
        times = pd.date_range(f"{year}-01-01", f"{year+1}-01-01",
                              freq="h", inclusive="left", tz="UTC")
        for state, value in (("CA", 100.0), ("NV", 40.0)):
            frames.append(pd.DataFrame({"timestamp_utc": times,
                                        "state": state, "load_mw": value}))
    load = pd.concat(frames, ignore_index=True)
    load_path = tmp_path / "load.csv"
    weights_path = tmp_path / "weights.csv"
    load.to_csv(load_path, index=False)
    pd.DataFrame([("CA", "CA_A", 0.25), ("CA", "CA_B", 0.75),
                  ("NV", "NV_A", 1.0)], columns=["state", "zone", "weight"]
                 ).to_csv(weights_path, index=False)
    out = tmp_path / "zones.csv"
    result = export_zonal_loads(load_path, weights_path, tmp_path / "audit.csv",
                                out, require_provenance=False)
    assert out.exists()
    assert len(result) == (8760 + 8784) * 3
    assert set(result.zone) == {"CA_A", "CA_B", "NV_A"}
    assert pd.to_datetime(result.timestamp_utc, utc=True).nunique() == 8760 + 8784
    np.testing.assert_allclose(result.load_mw.sum(), load.load_mw.sum(), atol=1e-5)
