"""County-native ReEDS renewable-to-state mapping; no BA-border allocation.

The published county files use resource class and five-digit county FIPS.
Join *exact* resource class/region keys to publisher supply curves before
calling this module. It does not transform instantaneous CF into hour energy.
"""
from __future__ import annotations
import re
import numpy as np
import pandas as pd

STATES={"AZ":"04","CO":"08","ID":"16","WY":"56"}
WIND_COUNTY_MD5="0670813d0a18b688d698ca24cf67fb92"
PV_COUNTY_MD5="aba834ea4c592023bca47de2ba79e7ec"
WIND_COUNTY_CAPACITY_MD5="49ab4e41dc386453b5fd32e5810774d4"
PV_COUNTY_CAPACITY_MD5="e10b1a64f3a67d163e739b735938eb78"
PV_ILR=1.34


def parse_county_columns(names):
    """ReEDS source labels are resource class|p<5-digit FIPS>."""
    rows=[]
    for name in names:
        if isinstance(name, bytes):
            name=name.decode("utf-8")
        match=re.fullmatch(r"([^|]+)\|p(\d{5})",str(name))
        if match is None:
            raise ValueError(f"Not an unambiguous county-resource label: {name}")
        rows.append((str(name),match.group(1),match.group(2),
                     match.group(2)[:2]))
    result=pd.DataFrame(rows,columns=["column","resource_class","county_fips","state_fips"])
    if result.column.duplicated().any():
        raise ValueError("Duplicate official county resource-class keys")
    return result


def validate_capacity_key_match(profile_names, supply_keys, supply_mw, *,
                                capacity_basis, tech):
    """One exact capacity row per HDF5 class/county key; no assumed row order."""
    profile=parse_county_columns(profile_names)
    caps=pd.DataFrame({"column":list(supply_keys),"capacity_mw":list(supply_mw)})
    if caps.column.duplicated().any():
        raise ValueError("Duplicate supply-curve class/county rows")
    if set(profile.column)!=set(caps.column):
        raise ValueError("Supply curve resource keys do not match HDF5 columns")
    caps.capacity_mw=pd.to_numeric(caps.capacity_mw,errors="raise")
    if not np.isfinite(caps.capacity_mw).all() or (caps.capacity_mw < 0).any():
        raise ValueError("Invalid supply curve capacity in MW")
    if tech=="pv" and capacity_basis not in ("dc","ac"):
        raise ValueError("PV capacity denominator (DC or AC) must be authenticated")
    if tech=="wind" and capacity_basis!="ac":
        raise ValueError("Wind installed MW basis must be AC")
    if tech not in ("pv","wind"):
        raise ValueError("Unsupported technology")
    return profile.merge(caps,on="column",validate="one_to_one",sort=False)


def state_cf_from_county_resource_matrix(values, column_table, *, tech,
                                         native_cf_scale=None,
                                         pv_capacity_basis=None):
    """Capacity-weighted state instantaneous CF. No energy-interval claims.

    PV DC capacity uses source MW_AC_grid/MW_DC_array directly.
    PV AC capacity needs 1.34*source CF; no double-conversion.
    """
    arr=np.asarray(values)
    if arr.ndim!=2 or arr.shape[1]!=len(column_table):
        raise ValueError("CF matrix and resource/capacity table disagree")
    if np.issubdtype(arr.dtype,np.integer) and native_cf_scale is None:
        raise ValueError("Integer encoded CF requires authenticated source scale")
    if native_cf_scale is None:
        native_cf_scale=1.0
    if not np.isfinite(native_cf_scale) or native_cf_scale<=0:
        raise ValueError("Invalid CF encoding scale")
    cf=arr.astype(np.float64)/native_cf_scale
    if not np.isfinite(cf).all() or (cf<0).any() or (cf>1+1e-8).any():
        raise ValueError("Native CF outside [0,1]")
    if tech=="pv":
        if pv_capacity_basis not in ("dc","ac"):
            raise ValueError("Unknown PV denominator")
        if pv_capacity_basis=="ac":
            cf=cf*PV_ILR
            if (cf>1+1e-8).any():
                raise ValueError("AC-nameplate PV CF above 1")
    elif tech!="wind":
        raise ValueError("Unknown technology")

    output={}
    source_states=column_table["state_fips"].to_numpy()
    caps=column_table["capacity_mw"].to_numpy(dtype=float)
    if len(caps)!=cf.shape[1]:
        raise ValueError("Missing capacity weights")
    for state,fips in STATES.items():
        mask=source_states==fips
        if not mask.any() or caps[mask].sum()<=0:
            raise ValueError(f"No positive certified {tech} supply curve MW for {state}")
        # Each county stays wholly in its official state; no BA cross-border split.
        output[state]=cf[:,mask]@caps[mask]/caps[mask].sum()
    return pd.DataFrame(output)


def reject_uncertified_hour_energy_join():
    raise ValueError(
        "BLOCK_PHYSICAL_JOIN: publisher county-level instantaneous CF is "
        "not yet a demand hour-ending interval-energy profile"
    )
