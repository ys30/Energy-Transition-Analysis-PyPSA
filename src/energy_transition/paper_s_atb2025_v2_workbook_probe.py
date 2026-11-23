"""Provenance-only scan of the updated 2025 ATB v2 workbook.
This script does not claim to extract official 2030 storage CAPEX values.
"""
from __future__ import annotations
import argparse,hashlib,json,re,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def inspect(path):
    path=Path(path)
    if path.name!="2025_v2_Workbook_11-11-2026.xlsx":
        raise ValueError("Only the 2025 ATB revised v2 workbook is admitted")
    digest=hashlib.sha256()
    with path.open("rb") as src:
        for b in iter(lambda:src.read(1024*1024),b""):digest.update(b)
    with zipfile.ZipFile(path) as f:
        names=set(f.namelist())
        if not {"xl/workbook.xml","xl/_rels/workbook.xml.rels","[Content_Types].xml"}.issubset(names):
            raise ValueError("Not an ATB Excel workbook: package structure invalid")
        root=ET.fromstring(f.read("xl/workbook.xml"))
        sheets=[tag.attrib["name"] for tag in root.findall(".//m:sheets/m:sheet",NS)]
        if not sheets:raise ValueError("Missing workbook worksheets")
        matches=[];nstrings=0
        if "xl/sharedStrings.xml" in names:
            strings=ET.fromstring(f.read("xl/sharedStrings.xml"))
            for i,si in enumerate(strings.findall("m:si",NS)):
                s="".join(x.text or "" for x in si.findall(".//m:t",NS))
                nstrings+=1
                if re.search(r"battery|storage|utility.scale|2030|advanced|moderate|conservative",s,re.I):
                    if len(matches)<300:matches.append({"index":i,"text":s[:250]})
        return {"status":"OFFICIAL_ATB2025_V2_XLSX_PACKAGE_AUDITED",
            "source_file":path.name,"sha256":digest.hexdigest(),
            "source_release":"2025 v2 (November 11 2026)",
            "source_url":"https://data.openei.org/files/8759/2025_v2_Workbook_11-11-2026.xlsx",
            "sheet_count":len(sheets),"worksheet_names":sheets,
            "shared_string_count":nstrings,"matched_candidate_strings":matches,
            "official_2030_4h_8h_costs_verified":False,
            "cost_model_annualization_performed":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--workbook",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    m=inspect(a.workbook)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"paper_s_ATB2025_v2_source_inventory.json").write_text(json.dumps(m,indent=2)+"\n")
    print("PAPER_S_ATB2025_REVISED_V2_SOURCE_INVENTORY_PASS",m["sha256"],m["sheet_count"])

if __name__=="__main__":main()
