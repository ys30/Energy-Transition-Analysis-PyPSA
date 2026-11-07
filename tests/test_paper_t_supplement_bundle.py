import json
from pathlib import Path
import pandas as pd
import pytest
from energy_transition.paper_t_supplement_bundle import SOURCE_FILES,assemble,SOURCE_RUNS

def fixture(tmp_path):
    folders={k:tmp_path/k for k in SOURCE_RUNS}
    for directory in folders.values():directory.mkdir()
    years=(2030,2040,2050)
    states=("AZ","CA","CO","ID","MT","NM","NV","OR","UT","WA","WY")
    source={
       "lag_33_pairs":pd.DataFrame([
         {"year":y,"state":s,"best_nonwrap_offset":-3 if s in ("CA","NV","OR","WA") else -2,
          "best_nonwrap_mae_mw":17 if s=="ID" else .25} for y in years for s in states]),
       "idaho_subsectors":pd.DataFrame([
         {"Year":y,"Sector":"Sector"+str(i//7),"Subsector":"Sub"+str(i),
          "original_load_mwh":1000} for y in years for i in range(14)]),
       "idaho_frozen":pd.DataFrame([{"planning_year":y,"heldout_improvement_mw":2} for y in years]),
       "idaho_marginals":pd.DataFrame([
         {"year":y,"state":s,"group_type":typ,"reference_index_label":h,
          "mean_absolute_error_mw":5.} for y in years for s in ("ID","AZ","CA")
         for typ,values in (("month",range(1,13)),("hour",range(24))) for h in values]),
       "idaho_overview":pd.DataFrame([{"year":y,"state":s,"mae_mw":1} for y in years for s in ("ID","AZ","CA")]),
    }
    for key,(group,basename,_) in SOURCE_FILES.items():
        path=folders[group]/basename
        if key in source:source[key].to_csv(path,index=False)
        elif key.endswith("_provenance"):path.write_text(json.dumps({"test":True}))
        else:path.write_bytes(("figure fixture "+key+"\n").encode()*200)
    return folders

def test_assembled_bundle_has_hashes_source_runs_and_all_figures(tmp_path):
    folders=fixture(tmp_path);out=tmp_path/"bundle"
    m=assemble(folders,out)
    assert m["source_files_count"]==16
    assert m["source_lag_state_year_pairs"]==33
    assert m["source_idaho_subsector_year_rows"]==42
    assert m["source_idaho_month_hour_marginal_rows"]==324
    assert not m["permanent_archival_DOI_registered"]
    assert len(list((out/"figures").glob("*.svg")))==4
    assert len(list((out/"figures").glob("*.png")))==4
    assert len((out/"SHA256SUMS.txt").read_text().splitlines())==16

def test_fail_closed_missing_a_source_file(tmp_path):
    folders=fixture(tmp_path)
    (folders["lags"]/"efs_2020_2022_nonwrap_33_pairs.csv").unlink()
    with pytest.raises(ValueError,match="Expected one actual source"):
        assemble(folders,tmp_path/"out")

def test_fail_closed_missing_a_source_month_hour_bin(tmp_path):
    folders=fixture(tmp_path)
    path=folders["marginals"]/"source_month_hour_residual_groups.csv"
    df=pd.read_csv(path).iloc[:-1];df.to_csv(path,index=False)
    with pytest.raises(ValueError,match="Marginal reference 324"):
        assemble(folders,tmp_path/"out")
