"""Find physical AC-line paths between actual EFS-loaded Western buses.

Searches the original rated line graph; does not redistribute load or solve OPF.
"""
import argparse
import json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd
import pypsa


def audit(network, max_hops=15):
    n = pypsa.Network(str(network))
    lines = n.lines.copy()
    for key in ("r", "x", "s_nom"):
        lines[key] = pd.to_numeric(lines[key], errors="coerce")
    eligible = lines.loc[
        np.isfinite(lines.r) & lines.r.ge(0)
        & np.isfinite(lines.x) & lines.x.gt(0)
        & np.isfinite(lines.s_nom) & lines.s_nom.ge(100)
    ]
    graph = nx.Graph()
    for line_id, row in eligible.iterrows():
        u, v = str(row.bus0), str(row.bus1)
        if u == v:
            continue
        if not graph.has_edge(u, v) or float(row.s_nom) > graph[u][v]["rating"]:
            graph.add_edge(u, v, line_id=str(line_id), rating=float(row.s_nom))
    profiles = n.loads_t.p_set
    energy = {}
    for bus, group in n.loads.groupby(n.loads.bus.astype(str)):
        columns = list(group.index)
        value = float(profiles[columns].sum().sum())
        if np.isfinite(value) and value > 0:
            energy[str(bus)] = value
    loaded = sorted(energy)
    candidates = []
    for i, a in enumerate(loaded):
        if a not in graph:
            continue
        paths = nx.single_source_shortest_path(graph, a, cutoff=max_hops)
        for b in loaded[i + 1:]:
            if b not in paths:
                continue
            nodes = paths[b]
            edges = [graph[u][v] for u, v in zip(nodes, nodes[1:])]
            candidates.append({
                "load_bus_a": a, "load_bus_b": b,
                "hops": len(edges), "path_buses": nodes,
                "line_ids": [e["line_id"] for e in edges],
                "minimum_path_line_rating_mva": min(e["rating"] for e in edges),
                "load_a_annual_mwh": energy[a], "load_b_annual_mwh": energy[b],
                "source_network_line_graph": True,
                "dispatch_optimized": False,
                "path_thermal_feasibility_verified": False,
            })
    candidates.sort(key=lambda x: (x["hops"], -min(x["load_a_annual_mwh"], x["load_b_annual_mwh"])))
    return {
        "eligible_rated_ac_lines": len(eligible),
        "positive_efs_load_buses": len(loaded),
        "loaded_buses_present_in_rated_ac_graph": sum(b in graph for b in loaded),
        "max_hops_searched": max_hops,
        "admissible_ac_line_path_pairs": len(candidates),
        "top_candidate_paths": candidates[:20],
        "at_least_one_multiload_path_found": bool(candidates),
        "selection_scope": "AC lines with finite r >= 0, x > 0 and s_nom >= 100; no transformer/link traversal",
        "warning": "Graph connectivity is only a structural prerequisite. Excluded branches, AC physics, bus-level supply, timezones, and boundary injections are not validated.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-hops", type=int, default=15)
    args = parser.parse_args()
    if not 1 <= args.max_hops <= 100:
        raise ValueError("max-hops must be in 1..100")
    result = audit(args.network, args.max_hops)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
