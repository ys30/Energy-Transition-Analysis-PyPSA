"""Traceable, deliberately non-inferential source-cell inventory for ATB v2.

Exports row/column/cached-value/formula evidence from relevant ATB 2025 v2
worksheets to permit a separately reviewed six-record (2030 x 4/8-hour x
Advanced/Moderate/Conservative) CAPEX+FOM extract. Inventory is not a cost model.
"""
from __future__ import annotations
import argparse, hashlib, json, re, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

M="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR="http://schemas.openxmlformats.org/package/2006/relationships"
TARGET_SHEETS=("Utility-Scale Battery - R&D","Utility-Scale Battery - Expand",
               "Summary_CAPEX","Summary_FOM")
SOURCE="https://data.openei.org/files/8759/2025_v2_Workbook_11-11-2026.xlsx"
REQUIRED_SHA256="c3cece683ecbc943ac7170cbe668e4efdc5367731fe0bce83ee34bb359970b56"

def shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(x.text or "" for x in si.iter(f"{{{M}}}t"))
            for si in root.findall(f"{{{M}}}si")]

def sheet_paths(z):
    book=ET.fromstring(z.read("xl/workbook.xml"))
    rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid_to_path={}
    for node in rels.findall(f"{{{PR}}}Relationship"):
        target=node.attrib.get("Target","")
        if target.startswith("/"):target=target.lstrip("/")
        elif not target.startswith("xl/"):target="xl/"+target
        rid_to_path[node.attrib["Id"]]=target
    out={}
    for node in book.findall(f".//{{{M}}}sheet"):
        rid=node.attrib.get(f"{{{R}}}id")
        if rid in rid_to_path:out[node.attrib["name"]]=rid_to_path[rid]
    return out

def read_rows(z,path,strings):
    root=ET.fromstring(z.read(path))
    for node in root.findall(f".//{{{M}}}sheetData/{{{M}}}row"):
        cells=[]
        for c in node.findall(f"{{{M}}}c"):
            typ=c.attrib.get("t")
            raw=c.find(f"{{{M}}}v")
            formula=c.find(f"{{{M}}}f")
            val=raw.text if raw is not None else None
            if typ=="s" and val is not None:
                idx=int(val)
                if idx>=len(strings):raise ValueError("Invalid shared string index")
                val=strings[idx]
            if typ=="inlineStr":
                val="".join(x.text or "" for x in c.iter(f"{{{M}}}t"))
            if val is not None or formula is not None:
                cells.append({"cell":c.attrib.get("r"),
                              "cached_value":val,
                              "formula":formula.text if formula is not None else None})
        if cells:yield int(node.attrib["r"]),cells

def inspect(src):
    path=Path(src)
    if path.name!="2025_v2_Workbook_11-11-2026.xlsx":
        raise ValueError("Incorrect ATB edition filename")
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    if sha!=REQUIRED_SHA256:raise ValueError("ATB v2 publisher SHA-256 mismatch")
    with zipfile.ZipFile(path) as z:
        paths=sheet_paths(z)
        if not all(n in paths for n in TARGET_SHEETS):
            raise ValueError("Missing official battery or summary sheet")
        strings=shared_strings(z)
        inventory={}
        terms=re.compile(r"2030|4.hour|8.hour|battery|storage|advanced|moderate|conservative|capex|FOM|OCC",re.I)
        for name in TARGET_SHEETS:
            selected=[];found=0;row_count=0
            for number,cells in read_rows(z,paths[name],strings):
                row_count+=1
                values=" ".join(str(c["cached_value"] or "") for c in cells)
                if number<=60 or terms.search(values):
                    found+=1
                    if len(selected)<180:
                        selected.append({"row":number,"cells":cells[:42],
                                         "cell_count":len(cells)})
            inventory[name]={"source_xml_path":paths[name],
                             "nonempty_rows":row_count,"selected_rows_total":found,
                             "selected_rows_exported":len(selected),
                             "selected_rows":selected}
    return {"status":"ATB2025_V2_BATTERY_CELL_LAYOUT_SOURCE_VERIFIED",
            "sha256":sha,"source_url":SOURCE,"release_date":"2026-11-11",
            "sheets":inventory,
            "official_2030_storage_costs_extracted_and_validated":False,
            "unverified_values_inferred":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--workbook",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    m=inspect(a.workbook)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"paper_s_ATB2025_v2_battery_cell_layout.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print("PAPER_S_ATB2025_V2_BATTERY_LAYOUT_VERIFIED",m["sha256"])
    for n,s in m["sheets"].items():
        print(n,s["nonempty_rows"],s["selected_rows_exported"])

if __name__=="__main__":main()
