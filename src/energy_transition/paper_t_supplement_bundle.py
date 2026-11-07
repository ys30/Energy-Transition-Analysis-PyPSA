"""Build a hash-verified Paper T supplementary evidence bundle.

Actual data and figures are retrieved from previously passing GitHub Actions
source artifacts. We do not reconstruct missing source rows or invent joint
month×hour observations. The bundle is not a permanent archive/DOI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import pandas as pd

SOURCE_FILES={
 "lag_33_pairs":("lags","efs_2020_2022_nonwrap_33_pairs.csv","tables/T_S1_nonwrapping_33_state_year_lags.csv"),
 "idaho_subsectors":("subsectors","idaho_source_subsector_annual_energy.csv","tables/T_S2_idaho_original_subsector_annual_energy.csv"),
 "idaho_frozen":("subsectors","idaho_frozen_2030_transport_shift_crossyear.csv","tables/T_S3_idaho_frozen_transport_crossyear.csv"),
 "idaho_marginals":("marginals","source_month_hour_residual_groups.csv","tables/T_S4_idaho_reference_month_hour_marginals.csv"),
 "idaho_overview":("marginals","source_state_year_residual_overview.csv","tables/T_S5_idaho_source_residual_overview.csv"),
 "lag_provenance":("lags","efs_2020_2022_nonwrap_metadata.json","provenance/nonwrapping_lag_source.json"),
 "idaho_subsector_provenance":("subsectors","idaho_subsector_source_provenance.json","provenance/idaho_subsector_original_source.json"),
 "idaho_marginal_provenance":("marginals","source_residual_diagnostic_provenance.json","provenance/idaho_marginal_original_source.json"),
 "figure_T1_svg":("t1","figure_T1_source_admission.svg","figures/figure_T1_source_admission.svg"),
 "figure_T1_png":("t1","figure_T1_source_admission.png","figures/figure_T1_source_admission.png"),
 "figure_T2_svg":("t24","figure_T2_source_lag_2030.svg","figures/figure_T2_source_lag_2030.svg"),
 "figure_T2_png":("t24","figure_T2_source_lag_2030.png","figures/figure_T2_source_lag_2030.png"),
 "figure_T3_svg":("t3","figure_T3_idaho_month_hour_marginals.svg","figures/figure_T3_idaho_month_hour_marginals.svg"),
 "figure_T3_png":("t3","figure_T3_idaho_month_hour_marginals.png","figures/figure_T3_idaho_month_hour_marginals.png"),
 "figure_T4_svg":("t24","figure_T4_frozen_shift_holdout.svg","figures/figure_T4_frozen_shift_holdout.svg"),
 "figure_T4_png":("t24","figure_T4_frozen_shift_holdout.png","figures/figure_T4_frozen_shift_holdout.png"),
}
SOURCE_RUNS={"lags":42122065064,"subsectors":42131969905,
             "marginals":42125517759,"t1":42177083314,
             "t24":42145896229,"t3":42162565936}

def unique_file(directory:Path,name:str)->Path:
    candidates=[p for p in directory.rglob(name) if p.is_file()]
    if len(candidates)!=1:
        raise ValueError(f"Expected one actual source file {directory}/{name}; found {len(candidates)}")
    return candidates[0]

def assemble(inputs:dict[str,Path],out:Path)->dict:
    out.mkdir(parents=True,exist_ok=True)
    copied=[]
    for key,(group,basename,target) in SOURCE_FILES.items():
        if group not in inputs:raise ValueError("Missing independently archived group "+group)
        source=unique_file(inputs[group],basename)
        dest=out/target
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
        digest=hashlib.sha256(dest.read_bytes()).hexdigest()
        copied.append({"key":key,"file":target,"sha256":digest,
                       "bytes":dest.stat().st_size,"verified_source_run_id":SOURCE_RUNS[group]})
    lag=pd.read_csv(out/"tables/T_S1_nonwrapping_33_state_year_lags.csv")
    subsector=pd.read_csv(out/"tables/T_S2_idaho_original_subsector_annual_energy.csv")
    frozen=pd.read_csv(out/"tables/T_S3_idaho_frozen_transport_crossyear.csv")
    marginals=pd.read_csv(out/"tables/T_S4_idaho_reference_month_hour_marginals.csv")
    overview=pd.read_csv(out/"tables/T_S5_idaho_source_residual_overview.csv")
    if len(lag)!=33 or lag[["year","state"]].drop_duplicates().shape[0]!=33:
        raise ValueError("33-year-state lag population failed")
    if set(lag.year)!={2030,2040,2050} or lag.groupby("year").state.nunique().ne(11).any():
        raise ValueError("Incomplete original lag years or states")
    if len(subsector)!=42 or subsector[["Sector","Subsector"]].drop_duplicates().shape[0]!=14:
        raise ValueError("Idaho original 14 source subsectors ×3 years failed")
    if set(subsector.Year)!={2030,2040,2050}:raise ValueError("Subsector original years incomplete")
    if len(frozen)!=3 or set(frozen.planning_year)!={2030,2040,2050}:
        raise ValueError("Frozen source candidate cross-year coverage failed")
    if len(marginals)!=324 or marginals[["year","state","group_type","reference_index_label"]].duplicated().any():
        raise ValueError("Marginal reference 324 rows incomplete")
    if len(overview)!=9 or set(overview.state)!={"ID","AZ","CA"}:
        raise ValueError("Residual source state-year comparison incomplete")
    manifest={
      "status":"ORIGINAL_SOURCE_PAPER_T_SUPPLEMENT_VERIFIED",
      "format_version":"1",
      "paper":"T: Annual Agreement, Hourly Disagreement",
      "source_files_count":len(copied),
      "source_lag_state_year_pairs":33,
      "source_idaho_subsector_year_rows":42,
      "source_idaho_subsectors":14,
      "source_idaho_frozen_year_rows":3,
      "source_idaho_month_hour_marginal_rows":324,
      "figures":["T1","T2","T3","T4"],
      "all_four_figures_have_svg_and_png":True,
      "source_run_ids":SOURCE_RUNS,
      "files":copied,
      "physical_EFS2020_UTC_verified":False,
      "source_2020_weather_renewable_join_admitted":False,
      "Idaho_causal_timezone_explained":False,
      "permanent_archival_DOI_registered":False,
      "note":"GitHub Actions artifacts expire. This combined artifact is for coauthor reproducibility and must be deposited separately for a permanent DOI."
    }
    (out/"source_sha256_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    with (out/"SHA256SUMS.txt").open("w") as f:
        for item in copied:f.write(f"{item['sha256']}  {item['file']}\n")
    (out/"README.md").write_text(
      "# Paper T supplementary reproducibility evidence\n\n"
      "Tables T_S1–T_S5 and Figures T1–T4 are copied from source-validated GitHub Actions runs; "
      "checksums and originating run identifiers are in source_sha256_manifest.json.\n\n"
      "Run `sha256sum -c SHA256SUMS.txt` within this directory. "
      "Original EFS2020 physical UTC remains uncertified. "
      "This is a **temporary Actions archive** and is **not a permanent DOI deposit**.\n")
    return manifest

def main():
    parser=argparse.ArgumentParser()
    for name in SOURCE_RUNS:parser.add_argument("--"+name,required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    result=assemble({k:getattr(a,k) for k in SOURCE_RUNS},a.out)
    print(json.dumps({k:v for k,v in result.items() if k!="files"},indent=2))
if __name__=="__main__":main()
