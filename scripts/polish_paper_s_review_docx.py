"""Paper S reproducible final review DOCX polish.

Uses author-approved static paper numbers and graph anchors, does not alter LP source results.
Mathematical display graphics are rendered by Matplotlib; they are images,
not editable Word equation objects (journal production can replace with OMML).
"""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

EQ_POTENTIAL = (
    r"$w_{c,j,s}^{\mathrm{pot}}=\frac{\sum_k M_{c,k,j,s}^{\mathrm{pot}}}"
    r"{\sum_{c,k}M_{c,k,j,s}^{\mathrm{pot}}}$",
    r"$w_{c,j,s}^{\mathrm{EIA}}=\frac{M_{c,j,s}^{\mathrm{OP,2025}}}"
    r"{\sum_c M_{c,j,s}^{\mathrm{OP,2025}}}$",
)
EQ_ANNUITY = (
    r"$V_{4\to 8}=\frac{C_4-C_8}{1000\,(E_8-E_4)}"
    r"\quad \mathrm{USD/(kWh\cdot year)}$",
)
YEAR_TABLE = [
    ("2010","11.068 / 10.727","5.562 / 5.948","2.993 / 5.645","3.169 / 5.439"),
    ("2011","12.017 / 11.421","6.178 / 5.832","3.146 / 6.208","3.864 / 6.651"),
    ("2012","10.955 / 9.868","6.221 / 5.943","4.135 / 5.790","3.541 / 5.978"),
    ("2013","12.821 / 12.842","5.619 / 5.826","3.467 / 5.274","2.672 / 5.044"),
]
def math_picture(s,p,eqs,fig_dir):
    p.clear()
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before=Pt(4)
    p.paragraph_format.space_after=Pt(6)
    p.paragraph_format.keep_together=True
    for i,eq in enumerate(eqs):
        img=fig_dir/("paper_s_equation_"+str(len(eqs))+"_"+str(i)+".png")
        fig=plt.figure(figsize=(7,.52),dpi=260)
        fig.text(.5,.5,eq,ha="center",va="center",fontsize=18)
        fig.savefig(img,dpi=260,bbox_inches="tight",pad_inches=.08)
        plt.close(fig)
        p.add_run().add_picture(str(img),width=Inches(3.3 if len(eqs)==2 else 4.3))
        if i<len(eqs)-1:
            p.add_run("\n")

def polish(original,out):
    doc=Document(original)
    work=Path(out).parent
    work.mkdir(parents=True,exist_ok=True)
    potential=[p for p in doc.paragraphs if r"w_{c,j,s}^{pot}=" in p.text and r"\frac" in p.text]
    annuity=[p for p in doc.paragraphs if r"V_{4\to8}=" in p.text and r"\frac" in p.text]
    if len(potential)!=1 or len(annuity)!=1:
        raise ValueError("Expected exactly two visible source-LaTeX equation blocks")
    math_picture(doc,potential[0],EQ_POTENTIAL,work)
    math_picture(doc,annuity[0],EQ_ANNUITY,work)
    anchor=next((p for p in doc.paragraphs
                 if p.text.startswith("3.5. Paired source-hour approximation sensitivity")),None)
    if anchor is None:raise ValueError("Section 3.5 missing")
    cap=doc.add_paragraph("Table 1. Four historical ReEDS weather years × four states: marginal 4-to-8-hour storage operating-value ceilings (USD per added kWh-year) under the noncyclic trapezoid approximation. Entries are source resource-potential / EIA 2025 operating-county weights; hypothetical avoided variable costs only, not actual investment returns.")
    cap.style="Caption"
    anchor._p.addprevious(cap._p)
    tb=doc.add_table(rows=1,cols=5)
    tb.style="Light Shading Accent 1"
    tb.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,x in enumerate(("Weather year","Arizona","Colorado","Idaho","Wyoming")):
        tb.rows[0].cells[i].text=x
    for data in YEAR_TABLE:
        cells=tb.add_row().cells
        for i,x in enumerate(data):cells[i].text=x
    for row in tb.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.space_after=Pt(1)
                for run in para.runs:run.font.size=Pt(8.5)
    trPr=tb.rows[0]._tr.get_or_add_trPr()
    header=OxmlElement("w:tblHeader")
    header.set(qn("w:val"),"true")
    trPr.append(header)
    anchor._p.addprevious(tb._tbl)
    fig_head=next((p for p in doc.paragraphs if p.text=="Verified manuscript figures"),None)
    ref_head=next((p for p in doc.paragraphs if p.text=="References and original data sources"),None)
    reviewer=next((p for p in doc.paragraphs if p.text=="Reviewer-facing scope note"),None)
    if not all((fig_head,ref_head,reviewer)):
        raise ValueError("Expected figure, reference and review note sections")
    body=doc._body._body
    nodes=list(body)
    moving=nodes[nodes.index(fig_head._p):nodes.index(reviewer._p)]
    for element in moving:body.remove(element)
    for element in moving:ref_head._p.addprevious(element)
    for paragraph in list(doc.paragraphs):
        if paragraph.text=="Reviewer-facing scope note" or paragraph.text.startswith(
            "The analyses use instantaneous ReEDS resource capacity-factor samples"):
            paragraph._element.getparent().remove(paragraph._element)
    in_references=False
    for paragraph in doc.paragraphs:
        if paragraph.text=="References and original data sources":
            in_references=True
            continue
        if in_references and paragraph.text.startswith("["):
            paragraph.paragraph_format.space_after=Pt(4)
            for run in paragraph.runs:run.font.size=Pt(9)
    doc.save(out)
    d=Document(out)
    texts="\n".join(p.text for p in d.paragraphs)
    if len(d.tables)!=1 or len(d.inline_shapes)!=5 or r"\frac" in texts:
        raise ValueError("DOCX source formulas / table / figures admission failed")
    if not texts.index("Verified manuscript figures")<texts.index("References and original data sources"):
        raise ValueError("Figures must precede bibliography")
    print("PAPER_S_DOCX_FORMULA_TABLE_FIGURE_ORDER_QA_PASS",Path(out).stat().st_size)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    polish(a.input,a.out)
if __name__=="__main__":main()
