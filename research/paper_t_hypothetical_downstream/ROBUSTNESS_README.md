# Paper T: hypothetical downstream time-shift robustness

**SYNTHETIC-ONLY:** 60 computed combinations, not an observed grid effect or a physical hourly join of EFS2020 and ReEDS2022.

Four hypothetical solar multipliers (0.5, 1, 1.5, 2), five hypothetical demand evening-peak hours (16, 18, 19, 20, 22), and demand time shifts 0, -2, -3 h relative to a fixed solar curve. All shifts circularly preserve annual energy in a 365 × 24 synthetic index with no physical time-zone or DST semantics.

Run:
```bash
python research/paper_t_hypothetical_downstream/paper_t_robustness.py
python -m unittest discover -s research/paper_t_hypothetical_downstream -p 'test_*.py' -v
```

Results (20 configurations per lag):
| Lag | Net peak decreased | Unchanged | Increased | Peak change | Solar-overlap increased | Overlap change |
|---|---:|---:|---:|---:|---:|---:|
| −2 h | 12 | 8 | 0 | −8.7767% to 0% | 12 | −0.1199 to +3.1920 pp |
| −3 h | 16 | 4 | 0 | −11.0839% to 0% | 15 | 0 to +4.6632 pp |

Net peak = max(demand − solar). Solar overlap = sum(min(demand,solar)) / sum(solar). These are stylized descriptive metrics, not dispatch or measured curtailment. Because profiles are deliberately stylized and all tested shifts are negative, a lack of increases in this family does not establish a universal direction. Original EFS/ReEDS physical-hour admission gates remain blocked.

**Manuscript-ready interpretation:** Across 20 wholly synthetic demand–solar configurations, advancing the demand curve by 2 or 3 index hours changed peak net demand in 12 and 16 configurations, respectively, with magnitude sensitive to solar scale and demand peak timing. The direction and magnitude cannot be attributed to a measured Idaho or Western-grid impact without source-certified physical clocks.
