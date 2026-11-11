"""Fail-closed official EIA-860 2025 annual plant+generator Excel schema probe.

This validates release file names and worksheet columns only; it DOES NOT
derive a geographic plant fleet, guess plant/generator joins, or treat
ReEDS developable resource potential as actual installed capacity.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
from pathlib import Path
import openpyxl

YEAR=2025
PUBLISHER_URL="https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip"
REQUIRED_CATEGORIES={
 "plant":r"(?i)(?:^|/)2_+Plant2025\.(?:xlsx|xlsm)$",
 "generator":r"(?i)(?:^|/)3_1_Generator2025\.(?:xlsx|xlsm)$",
}
EXPECTED_STATE_LABELS=("AZ","CO","ID","WY")

def probe(zip_path,out):
    zip_path=Path(zip_path)
    digest=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    report={"year":YEAR,"official_release":PUBLISHER_URL,
       "observed_zip_sha256_not_publisher_signature":digest,
       "plant_county_link_certified":False,
       "operable_generator_filter_certified":False,
       "wind_and_PV_AC_nameplate_basis_certified":False,
       "EIA_2025_fleet_county_weights_extracted":False,
       "ReEDS2022_source_county_FIPS_join_certified":False,
       "2025_is_observed_2030_fleet":False,
       "candidate_workbooks":{}}
    with zipfile.ZipFile(zip_path) as z:
        names=[n for n in z.namelist() if not n.endswith("/")]
        for typ,pattern in REQUIRED_CATEGORIES.items():
            matches=[n for n in names if re.search(pattern,n)]
            if len(matches)!=1:raise ValueError(f"Expected exactly one source {typ} workbook, got {matches}")
            buf=io.BytesIO(z.read(matches[0]))
            book=openpyxl.load_workbook(buf,read_only=True,data_only=True)
            sheets=[]
            for sheet in book.worksheets:
                rows=[]
                for row in sheet.iter_rows(min_row=1,max_row=12,values_only=True):
                    vals=[str(v).strip() if v is not None else "" for v in row]
                    nonempty=[v for v in vals if v]
                    if len(nonempty)>=3:
                        rows.append({"row":len(rows)+1,"nonempty_columns_preview":nonempty[:40]})
                sheets.append({"sheet_name":sheet.title,"first_nonempty_rows_preview":rows[:6]})
            report["candidate_workbooks"][typ]={"archive_path":matches[0],"sheets":sheets}
    if not report["candidate_workbooks"]["plant"]["sheets"] or not report["candidate_workbooks"]["generator"]["sheets"]:
        raise ValueError("Official workbook sheet structures not resolved")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"paper_s_eia860_2025_plant_generator_schema_probe.json").write_text(json.dumps(report,indent=2)+"\n")
    print("OFFICIAL_EIA860_2025_PLANT_GENERATOR_SCHEMA_PROBE_COMPLETE_NOT_FLEET_CALIBRATED")
    print("plant:",[x["sheet_name"] for x in report["candidate_workbooks"]["plant"]["sheets"]])
    print("generator:",[x["sheet_name"] for x in report["candidate_workbooks"]["generator"]["sheets"]])
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    probe(a.zip,a.out)

if __name__=="__main__":
    main()
