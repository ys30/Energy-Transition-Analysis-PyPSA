"""Paper S figure S4 from source-derived nine year/shape marginal comparisons.

Plots are model-variable-objective and assumed renewable-potential reductions,
not investment returns, observed curtailment or verified Western grid impacts.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

YEARS = (2030, 2040, 2050)
SHAPES = ("flat_50pct", "ordinal24_wave_A", "ordinal24_wave_B")
METRICS = (
    ("unused_renewable_mwh", 1e6, "TWh", "Unused assumed renewable potential"),
    ("objective_illustrative_variable_usd", 1e9, "USD billion", "Illustrative LP variable objective"),
)
DISCLAIMER = "EFS projected demand + synthetic supply; no CAPEX, UTC certification or Western OPF."


def validate(frame: pd.DataFrame) -> pd.DataFrame:
    needed = {"planning_year", "synthetic_supply_shape", "zones", "source_ordinal_hours_per_case"}
    for metric, _, _, _ in METRICS:
        needed.update({
            f"{metric}_{h}h" for h in (0, 4, 8)
        })
        needed.update({
            f"{metric}_reduction_0to4h", f"{metric}_reduction_4to8h"
        })
    if not needed.issubset(frame):
        raise ValueError("Missing source-derived marginal columns")
    k = ["planning_year", "synthetic_supply_shape"]
    if (len(frame) != 9 or frame.duplicated(k).any() or
        set(frame.planning_year) != set(YEARS) or
        set(frame.synthetic_supply_shape) != set(SHAPES)):
        raise ValueError("Incomplete or duplicate nine annual/shape comparisons")
    if not frame.zones.eq(20).all() or not frame.source_ordinal_hours_per_case.eq(8760).all():
        raise ValueError("Invalid zone/year source coverage")
    for metric, _, _, _ in METRICS:
        cols = [f"{metric}_{h}h" for h in (0,4,8)]
        cols += [f"{metric}_reduction_{h}" for h in ("0to4h", "4to8h")]
        vals = frame[cols].to_numpy(dtype=float)
        if not np.isfinite(vals).all():
            raise ValueError("Nonfinite marginal or underlying source metric")
        if not np.allclose(vals[:,0]-vals[:,1], vals[:,3], atol=0.02, rtol=1e-10):
            raise ValueError("0-to-4 reduction does not match original result levels")
        if not np.allclose(vals[:,1]-vals[:,2], vals[:,4], atol=0.02, rtol=1e-10):
            raise ValueError("4-to-8 reduction does not match original result levels")
    return frame.sort_values(k).reset_index(drop=True)


def make_figures(frame: pd.DataFrame, out_dir: Path):
    data = validate(frame)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for metric, scale, unit, name in METRICS:
        fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.4), sharey=True)
        for ax, year in zip(axes, YEARS):
            yr = data[data.planning_year == year].set_index("synthetic_supply_shape").loc[list(SHAPES)]
            pos = np.arange(3)
            a = yr[f"{metric}_reduction_0to4h"].to_numpy(dtype=float)/scale
            b = yr[f"{metric}_reduction_4to8h"].to_numpy(dtype=float)/scale
            ax.bar(pos-.19, a, width=.38, label="0 to 4 hours", color="#3c78a8")
            ax.bar(pos+.19, b, width=.38, label="4 to 8 hours", color="#e59a41")
            ax.set_xticks(pos, ["Flat", "Wave A", "Wave B"])
            ax.set_title(str(year))
            ax.axhline(0,color="black",linewidth=.8)
            ax.grid(axis="y",alpha=.16)
            ax.set_axisbelow(True)
        axes[0].set_ylabel(f"Reduction in {name.lower()} ({unit})")
        axes[1].set_xlabel("Synthetic supply-availability profile")
        axes[0].legend(frameon=False, loc="best")
        fig.suptitle(f"Marginal 4-hour storage-duration increments: {name}", fontsize=12)
        fig.text(.5,.015,DISCLAIMER,ha="center",fontsize=8)
        fig.tight_layout(rect=[0,.05,1,.92])
        base = ("figure_S4_unused_potential" if metric == "unused_renewable_mwh"
                else "figure_S5_toy_variable_objective")
        for suffix in (".png", ".svg"):
            path = out_dir / (base + suffix)
            fig.savefig(path, dpi=220, bbox_inches="tight")
            files.append(path.name)
        plt.close(fig)
    return {"status":"PAPER_S_MARGINAL_FIGURES_FROM_ARCHIVED_540_CASES",
            "year_shape_comparisons":len(data), "files":files,
            "supply_profiles_empirical":False, "battery_capex_included":False,
            "utc_clock_certified":False, "western_opf":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--marginals",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    manifest=make_figures(pd.read_csv(a.marginals),a.out_dir)
    (a.out_dir/"paper_s_figure_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    main()
