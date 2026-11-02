# EIA-860 connection-evidence escalation: from geographic candidate to T&D owner to documented POI

## Source discovery (2026-11-01)

The PUDL normalized EIA yearly plants data dictionary includes `transmission_distribution_owner_id`, `transmission_distribution_owner_name`, and `transmission_distribution_owner_state`. This is useful intermediate evidence to organize interconnection research, but is **not** a documented source-network bus ID or substation tie.

Source: [PUDL yearly plants schema](https://data.catalyst.coop/preview/pudl/out_eia__yearly_plants).

The EIA-860 Form data dictionary separately describes an *Interconnection File* with project interconnection dates and location; consult the applicable vintage and primary form documentation before treating specific fields as available for a particular historical year. This too does not automatically establish identity with any PyPSA-USA bus.

Source: [EIA-860 Interconnection File field descriptions](https://downloads.regulations.gov/EPA-HQ-OW-2009-0819-1441/attachment_4.pdf).

## Evidence strength and dispatch admission

| Tier | Evidence | Does it prove a specific network bus tie? |
|---|---|---|
| G0 | Geographic nearest bus in same state | No |
| G1 | BA, utility or transmission/distribution owner linked via EIA/PUDL plant identity | No |
| G2 | Named point-of-interconnection facility/substation and voltage in primary utility, RTO/ISO or interconnection documentation | Identifies a physical interconnection target, **not yet** necessarily the PyPSA source bus ID |
| G3 | Auditable documented mapping from the physical POI to the exact source-network bus (including topology/voltage consistency) | Potentially yes, subject to quality review |

Treat the existing 89 unique EIA-860 candidate plants (79 recurring across 2023–2024) as the starting population for **G1–G3 evidence research**, not as already admissible electricity generators. The 2023 and 2024 review queues are retained as separate files and a deduplicated tracking table.

## Next reproducible operation

Join plant IDs in the year-specific queue to EIA/PUDL **yearly plant** identity and T&D owner fields for the matching year, using explicit vintage, one-to-one identity checks, missingness counts and documented source URLs. Do not assign a network bus, generator or optimizer availability from this owner-level match. Only promote to G2/G3 based on independently citable facility records and source-network bus evidence. If primary records are absent, record `not_verified` rather than guessing.

## Current gate

Zero electrical plant-to-PyPSA-bus links are verified; the demonstrated dual-EFS-load OPF still contains illustrative supply. Owner-level metadata provides a research avenue, not a dispatch calibration result.
