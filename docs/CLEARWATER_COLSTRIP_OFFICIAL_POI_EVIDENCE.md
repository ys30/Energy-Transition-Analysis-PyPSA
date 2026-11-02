# Clearwater wind: regulator-documented physical point of interconnection

## Verified external documentation — 2026-11-02

**Primary source:** Portland General Electric testimony filed with the Public Utility Commission of Oregon, **UE 427**, Exhibit PGE/100, available at https://edocs.puc.state.or.us/efdocs/HTB/ue427htb330150025.pdf (especially testimony pages 16–18 and Figure 1 on testimony page 17).

The regulatory testimony identifies the Clearwater project phases, including **Clearwater East** and **Clearwater III**, and states that **all phases connect to the existing NorthWestern Energy Colstrip 500 kV Substation via the approximately 100-mile Clearwater Resources generation tie line**. Figure 1 explicitly labels the Colstrip substation as **POI**, shows a **345 kV generation tie** and **345-to-500 kV transformation**. This is *documentary physical POI evidence*, materially stronger than nearest-neighbor geospatial matching.

Cross-reference to original EIA-860 annual generator records:
- EIA **66183 / CWE** — Clearwater Wind East, 207.9 MW wind, first reported operating **January 2024**.
- EIA **66811 / CW3** — Clearwater Wind III, 100.0 MW wind, first reported operating **September 2024**.

**Evidence tier:** regulator-filed project-level POI identified; **not yet** a verified EIA generator → specific original-PyPSA-bus electrical crosswalk. Do **not** put either row into the strict generator-to-bus gate as `independently_verified` until the model's actual bus ID, voltage, electrical topology, and relevant vintage have been inspected. Also distinguish physical NorthWestern BAA location from any PGE financial/pseudo-tie balancing authority treatment.

Additional source: 2025 federal FERC filing https://www.txnmenergy.com/~/media/Files/P/PNM-Resources/rates-and-filings/2025%20Blackstone%20Infrastructure/FERC/TXNM%20FERC%20203%20Application%20082525.pdf describes Clearwater III connection into Clearwater Resources interconnection transmission lines and Colstrip Transmission System.

### Next reproducible research gate
1. Retrieve the authoritative original PyPSA Western network buses and branches artifact, with source vintage and checksums.
2. Locate Colstrip Substation as an **explicit named/electrical** bus or documented constituent bus, not merely a nearby lat/lon.
3. Check 500-kV bus voltage, branch connectivity, power-flow connectivity, the Clearwater generation tie representation, and potential injection limit (note PGE's 300-MW *contracted* export restriction is not necessarily a shared all-phase physical limit).
4. Only then establish an audited EIA generator-to-model bus mapping with source URL and exact bus ID.

**Current verified generator-to-PyPSA-original-bus ties: 0.** **Current physical POI project families with regulator documentation: 1 (Clearwater).**
