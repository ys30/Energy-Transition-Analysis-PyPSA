"""Extract an EIA-860 plant-to-BA crosswalk from the *same* annual official ZIP.

Plant sheet keys, BA codes, duplicates and mismatches are audited; ambiguous
plants are excluded, never assigned by state.
"""
from __future__ import annotations
import argparse, io, json, urllib.request, zipfile
from pathlib import Path
import pandas as pd
from .eia860_capacity import URL, WESTERN_STATES
from .ba_crosswalk import normalize_plant_id, join_verified_crosswalk


def extract_plant_ba(archive: bytes):
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        names = [n for n in z.namelist() if n.lower().endswith((".xlsx", ".xls"))]
        matches = [n for n in names if Path(n).name.lower().startswith("2_") and "plant" in Path(n).name.lower()]
        if not matches:
            raise ValueError("Official EIA-860 ZIP is missing 2___Plant workbook")
        book = pd.ExcelFile(io.BytesIO(z.read(matches[0])))
        candidates = []
        for sheet in book.sheet_names:
            for h in (1, 0, 2):
                d = pd.read_excel(book, sheet_name=sheet, header=h)
                cols = {str(c).strip().lower(): c for c in d.columns}
                plant = next((v for k, v in cols.items() if k in ("plant code", "plant id", "plant id number")), None)
                ba = next((v for k, v in cols.items() if "balancing authority code" in k), None)
                state = cols.get("state")
                if plant and ba and state:
                    candidates.append((sheet, d, plant, ba, state))
                    break
            if candidates:
                break
        if not candidates:
            raise ValueError("Cannot resolve EIA-860 plant workbook Plant ID, BA code and state headers")
        sheet, d, plant, ba, state = candidates[0]
    x = d[[plant, ba, state]].copy()
    x.columns = ["plant_id", "ba_code", "state"]
    x["plant_id"] = normalize_plant_id(x.plant_id)
    x["ba_code"] = x.ba_code.astype("string").str.strip().str.upper()
    x["state"] = x.state.astype("string").str.strip().str.upper()
    x["crosswalk_qc"] = "valid"
    invalid = (x.plant_id.isna() | x.plant_id.eq("").fillna(True)
               | x.ba_code.isna() | x.ba_code.eq("").fillna(True))
    x.loc[invalid.fillna(True), "crosswalk_qc"] = "missing_plant_or_ba"
    valid = x.loc[x.crosswalk_qc.eq("valid")].copy()
    conflicting = valid.groupby("plant_id").ba_code.nunique().loc[lambda s:s.gt(1)].index
    x.loc[x.plant_id.isin(conflicting), "crosswalk_qc"] = "conflicting_ba"
    # A plant appearing under multiple states is also ambiguous even if the
    # reported BA code is identical; reject it before joining generators.
    conflicting_state = valid.groupby("plant_id").state.nunique().loc[lambda s:s.gt(1)].index
    x.loc[x.plant_id.isin(conflicting_state), "crosswalk_qc"] = "conflicting_plant_state"
    # Duplicate exact matches are redundant, not independent plants.
    return x, sheet


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=2024)
    p.add_argument("--generators", type=Path, required=True)
    p.add_argument("--local-zip", type=Path)
    p.add_argument("--output", type=Path, default=Path("outputs/eia860"))
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    url = URL.format(year=a.year)
    if a.local_zip:
        archive = a.local_zip.read_bytes()
    else:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"pypsa-west-benchmark/0.2"}), timeout=90) as response:
            archive = response.read()
    plants, sheet = extract_plant_ba(archive)
    plants.to_csv(a.output / f"plant_ba_raw_audit_{a.year}.csv", index=False)
    valid = plants.loc[plants.crosswalk_qc.eq("valid") & plants.state.isin(WESTERN_STATES)]
    valid = valid.drop_duplicates(["plant_id", "ba_code"])
    # Preserve the official annual crosswalk vintage for downstream reconciliation.
    crosswalk_export = valid[["plant_id", "ba_code"]].copy()
    crosswalk_export["mapping_year"] = a.year
    crosswalk_export.to_csv(a.output / f"plant_ba_crosswalk_{a.year}.csv", index=False)
    generators = pd.read_csv(a.generators, dtype={"plant_id": "string", "generator_id": "string"})
    joined = join_verified_crosswalk(generators, valid[["plant_id", "ba_code"]])
    joined.to_csv(a.output / f"generator_ba_audit_{a.year}.csv", index=False)
    mapped = joined[joined.crosswalk_status.eq("matched")].copy()
    # Never mix standby generator nameplate into operational capacity.
    if "status" in mapped:
        operating = mapped[mapped.status.astype(str).str.strip().eq("OP")]
    else:
        raise ValueError("Operational status must be present to estimate operating capacity")
    if operating.empty:
        raise ValueError("No operating generators matched to reported plant BA codes")
    if operating.capacity_mw.isna().any() or operating.capacity_mw.lt(0).any():
        raise ValueError("Invalid matched operating generator nameplate capacity")
    operating_all = joined.loc[
        joined.status.astype("string").str.strip().str.upper().eq("OP")
        & joined.capacity_mw.notna()
        & joined.capacity_mw.ge(0)
    ]
    operating_coverage = (
        float(operating.capacity_mw.sum()) / float(operating_all.capacity_mw.sum())
        if float(operating_all.capacity_mw.sum()) > 0 else 0.0
    )
    if operating_coverage < 0.95:
        raise ValueError(
            f"Operating nameplate BA crosswalk coverage {operating_coverage:.2%} "
            "below 95%; inspect generator_ba_audit before model calibration"
        )
    grouped = operating.groupby(["ba_code","fuel"], as_index=False).capacity_mw.sum()
    grouped.to_csv(a.output / f"ba_operating_nameplate_by_fuel_{a.year}.csv", index=False)
    report = {
        "source": url, "year": a.year, "plant_sheet": sheet,
        "plant_rows":len(plants), "valid_western_plant_rows":len(valid),
        "plant_qc_counts":{str(k):int(v) for k,v in plants.crosswalk_qc.value_counts().items()},
        "generator_rows":len(joined), "matched_generators":len(mapped),
        "unmatched_generators":int(joined.crosswalk_status.eq("unmatched").sum()),
        "operating_mapped_nameplate_mw":float(operating.capacity_mw.sum()),
        "operating_nameplate_mapping_fraction":operating_coverage,
        "boundary":"Only generator-plant joins with reported EIA-860 plant BA codes. This is not hourly availability or calibrated dispatch."
    }
    (a.output / f"ba_crosswalk_manifest_{a.year}.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__ == "__main__":
    main()
