"""Safely inventory EIA's official 2023 Form EIA-930A XLSX source.

Only workbook structure and the first source rows are exposed. This tool
does NOT infer generator capacity, fuel classification or BA crosswalk.
"""
from __future__ import annotations
import argparse,hashlib,json,re,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

SOURCE_URL="https://www.eia.gov/electricity/930-content/EIA_930A_2023_with%20layout.xlsx"
MAIN="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG="http://schemas.openxmlformats.org/package/2006/relationships"

def local(tag):return tag.rsplit("}",1)[-1]

def inspect(path,max_rows=18,max_cells=65):
    path=Path(path)
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        if "xl/workbook.xml" not in names:raise ValueError("Expected official XLSX workbook")
        shared=[]
        if "xl/sharedStrings.xml" in names:
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall(f"{{{MAIN}}}si"):
                shared.append("".join(x.text or "" for x in si.iter() if local(x.tag)=="t"))
        relations=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        paths={}
        for item in relations:
            r=item.attrib
            target=r.get("Target","")
            target=target.lstrip("/") if target.startswith("/xl/") else ("xl/"+target.lstrip("/") if not target.startswith("xl/") else target)
            paths[r.get("Id")]=target
        workbook=ET.fromstring(z.read("xl/workbook.xml"))
        results=[]
        for sheet in workbook.findall(f".//{{{MAIN}}}sheet"):
            name=sheet.attrib.get("name","")
            ref=sheet.attrib.get(f"{{{REL}}}id")
            worksheet=paths.get(ref)
            if worksheet not in names:raise ValueError("Sheet relationship is missing: "+name)
            root=ET.fromstring(z.read(worksheet))
            preview=[]
            total=0
            for row in root.findall(f".//{{{MAIN}}}sheetData/{{{MAIN}}}row"):
                total+=1
                if len(preview)>=max_rows:continue
                cells=[]
                for cell in row.findall(f"{{{MAIN}}}c")[:max_cells]:
                    value=cell.find(f"{{{MAIN}}}v")
                    inline=cell.find(f"{{{MAIN}}}is")
                    v=value.text if value is not None else ""
                    if cell.attrib.get("t")=="s" and v:
                        v=shared[int(v)]
                    if inline is not None:
                        v="".join(x.text or "" for x in inline.iter() if local(x.tag)=="t")
                    if v not in ("",None):
                        cells.append({"coordinate":cell.attrib.get("r"),"value":v[:180]})
                preview.append({"row":row.attrib.get("r"),"cells":cells})
            results.append({"sheet":name,"xml_path":worksheet,"total_rows":total,
                            "preview_rows":preview})
    return {"status":"OFFICIAL_2023_EIA930A_WORKBOOK_STRUCTURE_ONLY",
            "source_url":SOURCE_URL,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes":path.stat().st_size,
            "worksheets":results,"sheet_count":len(results),
            "BA_generator_crosswalk_authenticated":False,
            "capacity_by_BA_calculated":False,
            "observed_vs_ReEDS_RMSE_computed":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--file",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=inspect(a.file)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"eia930a_2023_official_workbook_structure.json").write_text(json.dumps(report,indent=2)+"\n")
    print("EIA930A_2023_SOURCE_WORKBOOK_STRUCTURAL_AUDIT_PASS",report["sheet_count"],report["sha256"])
if __name__=="__main__":main()
