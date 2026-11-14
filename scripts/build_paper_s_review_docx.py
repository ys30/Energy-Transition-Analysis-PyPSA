"""Build Paper S source-traceable review DOCX from integrated Markdown + verified figures.

Editorial review manuscript only: not independent physical energy certification or
a journal publisher's camera-ready template. Runs in GitHub Actions from repository
HEAD, never alters frozen LP results.
"""
from __future__ import annotations
import argparse,re
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION_START

SOURCE=Path("docs/PAPER_S_INTEGRATED_ENGLISH_MANUSCRIPT_V1_2026-11-12.md")
SKIP_HEADINGS={"Manuscript completion items (not scientific findings)"}
FIGURES=(
 ("paper_s_96lp_weather_x_county_siting_main_figure.png",
  "Figure 1. Historical weather × county siting: marginal 4→8-hour storage operating-value ceilings. Trapezoid point-to-hour approximation; see the 192-LP method sensitivity. The illustrative Arizona 2012 $10/kWh-year spatial screen crossing disappears under endpoint hold."),
 ("paper_s_96lp_weather_x_siting_difference_heatmap.png",
  "Figure 2. Difference between EIA 2025 operating county fractions and ReEDS resource-potential county weights in modeled 4→8-hour operating-value ceilings. Trapezoid mode. Geographic signed effects agree under endpoint hold for 15 of 16 historical state–weather cases; AZ 2013 is close to zero and changes sign."),
)

def inline_text(raw):
    s=re.sub(r"!\[([^]]*)\]\([^)]*\)",r"\1",raw)
    s=re.sub(r"\[([^]]+)\]\(([^)]+)\)",r"\1 (\2)",s)
    return s.replace("**","").replace("`","").replace("*","").strip()

def apply_style(doc):
    sec=doc.sections[0]
    sec.top_margin=Inches(.85);sec.bottom_margin=Inches(.8)
    sec.left_margin=Inches(.95);sec.right_margin=Inches(.95)
    normal=doc.styles["Normal"]; normal.font.name="Aptos"
    normal.font.size=Pt(10.5);normal.paragraph_format.space_after=Pt(7)
    normal.paragraph_format.line_spacing=1.12
    for name,size in (("Title",17),("Heading 1",13),("Heading 2",11.5),("Heading 3",10.5)):
        st=doc.styles[name];st.font.name="Aptos Display";st.font.size=Pt(size)
        st.font.color.rgb=RGBColor(30,50,70)
    header=sec.header.paragraphs[0]
    header.text="PAPER S  |  Source-audited storage operating-value sensitivity  |  REVIEW DRAFT"
    header.style="Caption"
    footer=sec.footer.paragraphs[0]
    footer.text="Original 96 LP: GitHub Actions 43281182390  •  Hour-method 192 LP: 43317414772"
    footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    footer.style="Caption"

def add_para(doc,line):
    v=inline_text(line)
    if v:doc.add_paragraph(v)

def make(source,figure_dir,out):
    raw=Path(source).read_text(encoding="utf-8").splitlines()
    doc=Document();apply_style(doc)
    doc.add_heading("Weather-Dependent Storage Duration Value under Renewable Resource Potential versus Observed County Siting",0)
    p=doc.add_paragraph("A Source-Audited Four-State U.S. Dispatch Study")
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Review manuscript • 13 November 2026 • Not a physically verified hour-integrated generation forecast").style="Subtitle"
    i=0;omit=False;equation=False;eq=[]
    while i<len(raw):
        line=raw[i].strip()
        if line.startswith("# Paper S"):
            i+=1;continue
        if line.startswith("**Working title:**") or line.startswith("**Manuscript status:**"):
            i+=1;continue
        if line.startswith("## "):
            label=line[3:].strip()
            omit=label in SKIP_HEADINGS
            if not omit:
                if label=="Verified candidate main-text figure captions (accepted external artifact)":
                    # External figure assets and their short captions will be inserted below.
                    omit=True
                else:doc.add_heading(label,level=1)
            i+=1;continue
        if omit:
            i+=1;continue
        if line.startswith("### "):doc.add_heading(line[4:],level=2);i+=1;continue
        if line=="\\[":
            equation=True;eq=[];i+=1;continue
        if line=="\\]" and equation:
            paragraph=doc.add_paragraph(" ".join(eq))
            paragraph.alignment=WD_ALIGN_PARAGRAPH.CENTER
            paragraph.style="Quote"
            equation=False;i+=1;continue
        if equation:
            eq.append(line);i+=1;continue
        if line.startswith("|") and i+1<len(raw) and raw[i+1].strip().startswith("|"):
            table_lines=[]
            while i<len(raw) and raw[i].strip().startswith("|"):
                table_lines.append(raw[i].strip());i+=1
            parsed=[[inline_text(cell) for cell in row.strip("|").split("|")] for row in table_lines]
            data=[row for row in parsed if not all(re.match(r"^:?-{3,}:?$",cell) for cell in row)]
            if data:
                t=doc.add_table(rows=1,cols=len(data[0]));t.style="Light Shading Accent 1"
                t.alignment=WD_TABLE_ALIGNMENT.CENTER
                for j,cell in enumerate(data[0]):t.rows[0].cells[j].text=cell
                for row in data[1:]:
                    cells=t.add_row().cells
                    for j,cell in enumerate(row[:len(cells)]):cells[j].text=cell
                doc.add_paragraph()
            continue
        if line and not line.startswith("---"):
            add_para(doc,line)
        i+=1
    available=[]
    for filename,caption in FIGURES:
        path=Path(figure_dir)/filename
        if not path.is_file() or path.stat().st_size<5000:
            raise ValueError(f"Verified figure missing: {path}")
        available.append(path)
    doc.add_page_break()
    doc.add_heading("Verified manuscript figures",level=1)
    for filename,caption in FIGURES:
        path=Path(figure_dir)/filename
        doc.add_picture(str(path),width=Inches(6.3))
        p=doc.add_paragraph(caption);p.style="Caption"
        doc.add_paragraph("Evidence: GitHub Actions 43288856607 (figure); 43317414772 (paired approximation sensitivity).").style="Caption"
    doc.add_heading("Reviewer-facing scope note",level=1)
    doc.add_paragraph("The analyses use instantaneous ReEDS resource capacity-factor samples and fixed 2030 projected demand. Hourly potential production is approximated by endpoint hold or noncyclic trapezoid, neither independently certified as physically integrated hourly energy. The system is a custom SciPy HiGHS copperplate LP with zero beginning and ending SOC; no verified future fleet, network congestion, project CAPEX, or financial returns are asserted.")
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    doc.save(out)
    print("PAPER_S_SOURCE_AUDITED_REVIEW_DOCX_CREATED",str(out),out.stat().st_size)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=SOURCE)
    p.add_argument("--figure-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make(a.source,a.figure_dir,a.out)

if __name__=="__main__":main()
