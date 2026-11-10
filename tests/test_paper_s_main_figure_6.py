import pandas as pd
import pytest
from energy_transition.paper_s_main_figure_6 import reconcile,plot

def source():
    annual=[];windows=[]
    for g,state,zone in ((1,"Arizona","p28"),(7,"Wyoming","p24")):
      for shape,p,e in (("flat_50pct",.25,1.),
                         ("ordinal24_wave_A",.125,.5),
                         ("ordinal24_wave_A",.25,1.),
                         ("ordinal24_wave_B",.25,1.)):
        annual.append({"source_shape_group":g,"state":state,"reeds_zone":zone,
          "synthetic_supply_shape":shape,"battery_power_peak_ratio":p,
          "battery_energy_peak_hours":e,"baseline":1000000.,
          "min":999999.,"max":1000001.,"width_mwh":2.})
      for window in ("early_1_168","middle_4001_4168"):
        windows.append({"source_shape_group":g,"state":state,"reeds_zone":zone,
            "window":window,"baseline":1000.,"min":800.,"max":1300.,
            "span_mwh":500.})
    return pd.DataFrame(annual),pd.DataFrame(windows)

def test_source_matched_comparison_and_figure(tmp_path):
    a,w=source()
    data=reconcile(a,w)
    assert len(data)==2
    assert (data.ratio_of_relative_spans>100).all()
    result=plot(a,w,tmp_path)
    assert result["matched_cases"]==2
    assert (tmp_path/"paper_s_proposed_main_Figure_6_annual_vs_window.svg").stat().st_size>1000

def test_mismatched_source_rejected():
    a,w=source();w.loc[1,"state"]="Other"
    with pytest.raises(ValueError,match="provenance"):reconcile(a,w)

def test_bad_interval_span_fails():
    a,w=source();a.loc[0,"width_mwh"]=500.
    with pytest.raises(ValueError,match="reconcile"):reconcile(a,w)
