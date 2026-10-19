# BLS injury & illness rates by NAICS industry, 2024 (CSV + JSON)

> **Free 3-year TRIR / DART / EMR prequal scorecard using this data: https://prequalrates.pages.dev**

This is a clean, machine-readable copy of the U.S. Bureau of Labor Statistics **Survey of Occupational Injuries and Illnesses (SOII), Table 1: Incidence rates of nonfatal occupational injuries and illnesses by industry and case types, 2024**. It covers 1,070 rows, including 1,024 private-industry NAICS codes, plus state and local government.

Contractor prequalification forms (ISNetworld, Avetta, GC and owner questionnaires) often ask whether your TRIR and DART are at or below the BLS average for your NAICS code. These are those averages.

## Files
| File | What it is |
|---|---|
| `data/bls_soii_2024_table1.csv` | One row per table row |
| `data/bls_soii_2024_table1.json` | Same rows, plus metadata (source, units, column list) |
| `scripts/parse_bls_table1.py` | Parser that rebuilds both files from the BLS HTML table |

## Columns
| Column | Meaning |
|---|---|
| `ownership` | `all_ownerships`, `private`, `state_and_local_government`, `state_government`, `local_government` |
| `naics` | NAICS 2017 code as printed by BLS (blank for aggregate rows such as "Goods-producing"; sector ranges like `31-33`) |
| `industry` | Industry title, with BLS footnote markers removed |
| `trc` | Total recordable cases rate. This is the "TRIR" benchmark |
| `dart` | Cases with days away from work, job restriction, or transfer (DART) |
| `dafw` | Cases with days away from work |
| `djtr` | Cases with job transfer or restriction only |
| `other_recordable` | Other recordable cases |
| `footnotes` / `footnote_text` | BLS footnote numbers on the row (e.g. `10` = fewer than 15 cases, `7` = rate rounded to zero, `8` = industry added in 2019) |
| `benchmark_naics`, `benchmark_trc`, `benchmark_dart` | Private rows only: the code whose rate to compare against. It equals `naics` unless BLS did not publish a TRC for that code |
| `is_parent_fallback` | `True` when the benchmark comes from the nearest parent code because BLS did not publish this code's rate (15 rows, e.g. 211 to 21) |

All rates are **cases per 100 full-time-equivalent workers**: (N ÷ EH) × 200,000. An empty value means BLS did not publish the figure (it doesn't meet publication guidelines).

## 3-year prequal math
- **TRIR** = total recordable cases × 200,000 ÷ total hours worked
- **DART** = (days-away cases + job transfer/restriction cases) × 200,000 ÷ total hours worked
- 200,000 = 100 full-time workers × 40 hours × 50 weeks

### Reading the OSHA 300A summary
| 300A column | Meaning | Used in |
|---|---|---|
| G | Deaths | TRIR |
| H | Cases with days away from work | TRIR, DART |
| I | Cases with job transfer or restriction | TRIR, DART |
| J | Other recordable cases | TRIR |
| Total hours worked | All employees' actual hours (exclude paid vacation, sick leave and holidays) | Denominator |

Total recordables = G + H + I + J. DART cases = H + I.

### Worked example: hours-weighted vs simple 3-year average
| Year | Recordables | Hours | Yearly TRIR |
|---|---|---|---|
| 1 | 1 | 40,000 | 5.00 |
| 2 | 0 | 120,000 | 0.00 |
| 3 | 1 | 140,000 | 1.43 |

- **Hours-weighted (combined) 3-year TRIR** = (1+0+1) × 200,000 ÷ 300,000 = **1.33**
- **Simple average of yearly rates** = (5.00 + 0.00 + 1.43) ÷ 3 = **2.14**

Same company, very different numbers. Use the method your form asks for and say which one you used. For a roofing contractor (NAICS 23816, 2024 TRC 2.4), this company passes on the weighted figure and also passes on the simple average.

## Source
U.S. Bureau of Labor Statistics, Survey of Occupational Injuries and Illnesses, in cooperation with participating state agencies. Table 1, 2024:
https://www.bls.gov/iif/nonfatal-injuries-and-illnesses-tables/table-1-injury-and-illness-rates-by-industry-2024-national.htm

Parsed 2026-10-19. Spot-checked against the official page (NAICS 23816, 212113, 311213, 5241, 62111), and a fresh parse of the live page that day produced an identical CSV. Read the BLS footnotes on the source page before relying on any single figure. Mining data come from MSHA, and the rail figures are not comparable with FRA's published data.

## License & status
- **Data:** BLS data are works of the U.S. federal government and in the **U.S. public domain**. This compilation is dedicated under **CC0 1.0**.
- **Scripts:** **MIT**. See `LICENSE`.
- **Not affiliated with, endorsed by, or reviewed by the U.S. Bureau of Labor Statistics or OSHA.** This is an independent copy; if anything differs, the official BLS table is authoritative.
