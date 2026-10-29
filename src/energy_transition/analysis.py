"""Synthetic multi-year electricity transition scenarios; NOT PyPSA solver output."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

YEARS = [2025, 2030, 2035, 2040]
TECH = ["Coal", "Gas", "Wind", "Solar"]
EMISSION_T_PER_MWH = {"Coal": 0.9, "Gas": 0.4, "Wind": 0., "Solar": 0.}

def scenario_data():
    values = [[45,30,15,10],[30,25,25,20],[15,20,35,30],[5,15,40,40]]
    df = pd.DataFrame(values,index=pd.Index(YEARS,name="year"),columns=TECH)
    assert (df.sum(axis=1)==100).all()
    return df

def metrics(df):
    renewable=df[["Wind","Solar"]].sum(axis=1)/df.sum(axis=1)
    emissions_mt=sum(df[t]*EMISSION_T_PER_MWH[t] for t in TECH)
    return pd.DataFrame({"renewable_share":renewable,"emissions_mtco2":emissions_mt})

def analyze(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    df=scenario_data();m=metrics(df)
    df.to_csv(output/"generation_twh.csv");m.to_csv(output/"metrics.csv")
    ax=df.plot(kind="bar",stacked=True,figsize=(9,5),rot=0)
    ax.set(ylabel="Electricity generation (TWh)",xlabel="Year",title="Illustrative generation mix — synthetic scenario")
    ax.legend(title="Technology",bbox_to_anchor=(1,1));ax.figure.tight_layout();ax.figure.savefig(output/"generation_mix.png",dpi=170);plt.close(ax.figure)
    fig,ax=plt.subplots(figsize=(8,4.5));ax.plot(m.index,m.renewable_share*100,marker="o");ax.set(xlabel="Year",ylabel="Renewable share (%)",title="Synthetic renewable generation share");ax.grid(alpha=.2);fig.tight_layout();fig.savefig(output/"renewable_share.png",dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5));ax.plot(m.index,m.emissions_mtco2,marker="o");ax.set(xlabel="Year",ylabel="Emissions (MtCO₂)",title="Synthetic operational CO₂ emissions");ax.grid(alpha=.2);fig.tight_layout();fig.savefig(output/"emissions.png",dpi=170);plt.close(fig)
    return {"renewable_share_2025":float(m.loc[2025,"renewable_share"]),"renewable_share_2040":float(m.loc[2040,"renewable_share"]),"emissions_2025_mt":float(m.loc[2025,"emissions_mtco2"]),"emissions_2040_mt":float(m.loc[2040,"emissions_mtco2"])}
