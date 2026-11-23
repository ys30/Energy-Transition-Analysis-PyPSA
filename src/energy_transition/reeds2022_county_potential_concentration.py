"""Paper S original ReEDS county source capacity concentration audit.

Uses strictly authenticated publisher 2012 county-class supply-curve MW
CSV, NEVER actual installed wind/PV county fleet. The equal-county
counterfactual simply gives every positive-resource county equal aggregate
weight and preserves published within-county class MW proportions.
This script does not read source HDF5 or recompute CF; it diagnoses
potential spatial representativeness only.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.reeds2022_county_state_resources import (
    STATES,parse_county_columns,WIND_COUNTY_CAPACITY_MD5,PV_COUNTY_CAPACITY_MD5,
)
from energy_transition.reeds2022_real_resource_intake import require_md5

DIGEST={"wind":WIND_COUNTY_CAPACITY_MD5,"pv":PV_COUNTY_CAPACITY_MD5}

def audit(county_csv,technology,*,verify_md5=True):
    if technology not in DIGEST:raise ValueError("Technology must be wind or pv")
    if verify_md5:require_md5(Path(county_csv),DIGEST[technology])
    x=pd.read_csv(county_csv,dtype=str)
    if list(x.columns)!=["class|region","MW"]:
        raise ValueError("Unexpected ReEDS county supply curve schema")
    table=parse_county_columns(x["class|region"].tolist())
    mw=pd.to_numeric(x["MW"],errors="raise").to_numpy(dtype=float)
    if len(mw)!=len(table) or not np.isfinite(mw).all() or (mw<0).any():
        raise ValueError("Invalid source potential MW")
    table["resource_potential_mw"]=mw
    rows=[]
    counties=[]
    for state,state_fips in STATES.items():
        t=table[table.state_fips.eq(state_fips)].copy()
        if t.empty:raise ValueError("Missing original county classes")
        county=t.groupby("county_fips",sort=True).resource_potential_mw.sum()
        county=county[county.gt(0)]
        k=len(county)
        if k==0:raise ValueError("State has no positive potential county")
        total=float(county.sum())
        potential_share=(county/total).to_numpy()
        equal_share=np.full(k,1/k)
        order=np.sort(potential_share)[::-1]
        hhi=float(np.square(potential_share).sum())
        concentration={
            "technology":technology,"state":state,
            "source_resource_class_count":len(t),
            "positive_potential_counties":k,
            "resource_potential_mw_original_basis":total,
            "resource_potential_capacity_basis":"MW_AC" if technology=="wind" else "MW_DC",
            "county_weight_scheme":"publisher_available_potential_not_installed",
            "largest_county_potential_fraction":float(order[0]),
            "top_five_counties_potential_fraction":float(order[:5].sum()),
            "HHI_county_potential_weights":hhi,
            "effective_potential_weighted_counties":float(1/hhi),
            "equal_county_effective_counties":k,
            "total_variation_distance_to_equal_county":float(.5*np.abs(potential_share-equal_share).sum()),
            "population_or_actual_fleet_calibrated":False,
        }
        rows.append(concentration)
        for county_fips,w in county.items():
            counties.append({"technology":technology,"state":state,"county_fips":county_fips,
                             "source_county_potential_mw":float(w),
                             "share_of_state_resource_potential":float(w/total),
                             "equal_positive_county_counterfactual_share":float(1/k),
                             "source_capacity_basis":"MW_AC" if technology=="wind" else "MW_DC"})
    return pd.DataFrame(rows),pd.DataFrame(counties)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--wind-capacity",type=Path,required=True)
    p.add_argument("--pv-capacity",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    all_stats,all_counties=[],[]
    for technology,path in (("wind",a.wind_capacity),("pv",a.pv_capacity)):
        stat,detail=audit(path,technology)
        all_stats.append(stat);all_counties.append(detail)
    stats=pd.concat(all_stats,ignore_index=True)
    county=pd.concat(all_counties,ignore_index=True)
    if len(stats)!=8 or len(county)==0 or stats.duplicated(["state","technology"]).any():
        raise ValueError("Incomplete four-state by two-technology potential weighting audit")
    if not np.allclose(county.groupby(["technology","state"]).share_of_state_resource_potential.sum(),1):
        raise ValueError("State source potential shares not conserved")
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    stats.to_csv(out/"paper_s_reeds2022_original_2012_county_potential_concentration_8.csv",index=False)
    county.to_csv(out/"paper_s_reeds2022_original_county_potential_weight_contrast.csv",index=False)
    manifest={
        "status":"AUTHENTICATED_REEDS_ORIGINAL_COUNTY_POTENTIAL_CONCENTRATION_AUDITED",
        "source_zenodo_wind":"https://zenodo.org/records/18422200",
        "source_zenodo_pv":"https://zenodo.org/records/18407660",
        "wind_source_MD5":WIND_COUNTY_CAPACITY_MD5,
        "pv_source_MD5":PV_COUNTY_CAPACITY_MD5,
        "state_technology_rows":len(stats),
        "county_rows":len(county),
        "weights_are_actual_installed_capacity":False,
        "county_equal_weights_are_actual_installed_capacity":False,
        "weather_hour_integral_certified":False,
        "LPs_completed":False,
        "resource_capacity_basis_mixed_wind_ac_PV_dc":True,
        "physical_allocation_and_spatial_validity_established":False,
    }
    (out/"paper_s_reeds2022_county_potential_concentration_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(stats[["state","technology","positive_potential_counties",
                 "effective_potential_weighted_counties",
                 "top_five_counties_potential_fraction",
                 "total_variation_distance_to_equal_county"]].to_string(index=False))
    print("SOURCE_AUTHENTICATED_COUNTY_WEIGHT_CONCENTRATION_DIAGNOSTICS_PASS")

if __name__=="__main__":
    main()
