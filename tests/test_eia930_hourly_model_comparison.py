import pandas as pd
import pytest
from energy_transition.eia930_hourly_model_comparison import compare_hourly


def test_hourly_comparison_measures_only_observed_common_hours():
    times=pd.date_range("2024-01-01",periods=3,freq="h",tz="UTC")
    observed=pd.DataFrame({"respondent":"CISO","period":times,"value":[10.,20.,30.]})
    modeled=pd.DataFrame({"respondent":"CISO","period":times[:2],"value":[12.,16.]})
    pairs, summary=compare_hourly(observed,modeled,2024,["CISO"])
    row=summary.iloc[0]
    assert row.expected_hours==8784
    assert row.observed_hours==3
    assert row.modeled_hours==2
    assert row.paired_hours==2
    assert row.mae_mw==3.0
    assert row.rmse_mw==(10.0)**0.5
    assert row.peak_absolute_error_mw==4.0
    assert row.mean_bias_mw==-1.0
    assert row.comparison_status=="partial_hours_not_calibrated"
    assert not row.validated_calibration
    assert pairs.model_minus_observed_mw.notna().sum()==2


def test_hourly_comparison_rejects_duplicate_and_off_hour_inputs():
    hour=pd.Timestamp("2024-01-01T00:00:00Z")
    observed=pd.DataFrame({"respondent":["CISO"],"period":[hour],"value":[10.]})
    dup=pd.concat([observed,observed],ignore_index=True)
    with pytest.raises(ValueError,match="duplicate BA-hour"):
        compare_hourly(dup,observed,2024,["CISO"])
    offset=observed.copy()
    offset.loc[0,"period"]=hour+pd.Timedelta(minutes=30)
    with pytest.raises(ValueError,match="non-hourly"):
        compare_hourly(observed,offset,2024,["CISO"])


def test_hourly_comparison_preserves_missing_not_zero_filled():
    hour=pd.Timestamp("2024-01-01T00:00:00Z")
    observed=pd.DataFrame({"respondent":["BPAT"],"period":[hour],"value":[None]})
    modeled=pd.DataFrame({"respondent":["BPAT"],"period":[hour],"value":[100.]})
    _,summary=compare_hourly(observed,modeled,2024,["BPAT"])
    row=summary.iloc[0]
    assert row.paired_hours==0
    assert pd.isna(row.mae_mw)
    assert row.comparison_status=="partial_hours_not_calibrated"


def test_extract_full_year_dispatch_rejects_representative_hours():
    from energy_transition.eia930_hourly_model_comparison import extract_full_year_dispatch
    from types import SimpleNamespace
    idx=pd.date_range("2024-01-01",periods=2,freq="h",tz="UTC")
    network=SimpleNamespace(
        snapshots=idx,
        generators=pd.DataFrame({"bus":["CISO"]},index=["CISO_gas"]),
        generators_t=SimpleNamespace(p=pd.DataFrame({"CISO_gas":[10.,20.]},index=idx)),
    )
    with pytest.raises(ValueError,match="Full-year hourly"):
        extract_full_year_dispatch(network,2024,["CISO"])


def test_extract_full_year_dispatch_sums_supported_generator_production():
    from energy_transition.eia930_hourly_model_comparison import extract_full_year_dispatch
    from types import SimpleNamespace
    idx=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    network=SimpleNamespace(
        snapshots=idx,
        generators=pd.DataFrame({"bus":["CISO","CISO","CISO"]},
             index=["CISO_gas","CISO_solar","CISO_unserved"]),
        generators_t=SimpleNamespace(p=pd.DataFrame(
             {"CISO_gas":10.,"CISO_solar":5.,"CISO_unserved":100.},index=idx)),
    )
    out=extract_full_year_dispatch(network,2024,["CISO"])
    assert len(out)==8784
    assert out.value.eq(15.).all()
    assert out.period.iloc[-1]==pd.Timestamp("2024-12-31T23:00:00Z")


def test_cli_reads_solved_full_year_network_without_expanding_representatives(tmp_path,monkeypatch):
    import sys
    from types import SimpleNamespace
    from energy_transition.eia930_hourly_model_comparison import main
    idx=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    network=SimpleNamespace(
        snapshots=idx,
        generators=pd.DataFrame({"bus":["CISO"]},index=["CISO_gas"]),
        generators_t=SimpleNamespace(p=pd.DataFrame({"CISO_gas":10.0},index=idx)),
    )
    monkeypatch.setitem(sys.modules,"pypsa",SimpleNamespace(Network=lambda path:network))
    observed=tmp_path/"observed.csv"
    pd.DataFrame({"respondent":"CISO","period":idx,"value":10.0}).to_csv(observed,index=False)
    monkeypatch.setattr(sys,"argv",[
        "hourly-compare","--observed",str(observed),
        "--network",str(tmp_path/"solved_network.nc"),
        "--year","2024","--bas","CISO","--output",str(tmp_path/"result"),
    ])
    main()
    summary=pd.read_csv(tmp_path/"result"/"ba_hourly_error_summary.csv").iloc[0]
    assert summary.paired_hours==8784
    assert summary.mae_mw==0.0
    assert summary.comparison_status=="complete_hourly_descriptive"
    assert not bool(summary.validated_calibration)
