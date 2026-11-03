# Western transmission topology: synthetic network provenance and limits

## Provenance (verified 2026-11-03)

The pinned PyPSA-USA source commit is `338af9912addbaf038c6098fe27e1e6ef099d8aa`. Its `workflow/scripts/build_base_network.py` reads the Breakthrough Energy source input tables `bus.csv`, `bus2sub.csv`, `sub.csv`, `branch.csv`, etc. The pinned `workflow/rules/retrieve.smk` downloads the source USATestSystem files from `https://zenodo.org/record/4538590/files/USATestSystem.zip`, writing inputs under `data/breakthrough_network/base_grid/`.

Source references:
- https://github.com/PyPSA/pypsa-usa/blob/338af9912addbaf038c6098fe27e1e6ef099d8aa/workflow/scripts/build_base_network.py
- https://github.com/PyPSA/pypsa-usa/blob/338af9912addbaf038c6098fe27e1e6ef099d8aa/workflow/rules/retrieve.smk
- https://pypsa-usa.readthedocs.io/en/stable/data-transmission.html
- https://pypsa-usa.readthedocs.io/en/stable/model-network-schema.html

## Interpretation

**This is a physically parameterized, synthetic nodal transmission test network with real-world geographical associations, NOT an independently verified inventory of operating transmission facilities.** Consequently:

- `bus_id` and `sub_id` are **source-model identifiers**, not utility-authenticated names or actual switchyard identifiers.
- Palo Verde's nearest 500-kV modeled bus `2040841` and source `sub_id=38478` are *unverified geographical/model-topology candidates*. Neither identifier can be presented as a confirmed Palo Verde point of interconnection.
- The 500-kV models' presence near Palo Verde does not prove actual facility identity; likewise the absence of an observed 115/230/500-kV model bus within 75 km of Grand Coulee does not imply the physical switchyards do not exist. Synthetic abstraction, voltage conventions, and topology source differences may explain the mismatch.
- The 2024 EIA-860 operating generator records and the synthetic bus population come from **different** source systems. Their geographic association is not proof of electrical connection.
- **No full-Western empirically validated OPF** can be claimed from this source until a verified plant-to-grid crosswalk and operational parameter validation are available. A synthetic-network OPF can be separately labeled as a simulation if the solver and assumptions are disclosed.

## Experimental framing

For the engineering benchmark, preserve three separate evidence tiers:

1. **Official generation inventory:** EIA-860/EIA-923 reported historical capacity/energy (qualified by source and period).
2. **Synthetic network modeling:** PyPSA-USA Breakthrough Energy/TAMU source-derived topology and electrical parameters; original node/transformer/line IDs retained for reproducibility.
3. **Independent physical POI validation:** absent until a source utility facility record, exact model-to-facility identity crosswalk and review establish one-to-one or justified many-to-one correspondence.

These distinctions take precedence over old descriptions that refer to the base `elec_base_network.nc` as simply a 'real Western network'.
