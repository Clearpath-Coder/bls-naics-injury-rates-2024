#!/usr/bin/env python3
"""Parse BLS SOII 2024 Table 1 (HTML) into CSV + JSON.
Usage: python3 scripts/parse_bls_table1.py path/to/table-1-...-2024-national.htm
Source: https://www.bls.gov/iif/nonfatal-injuries-and-illnesses-tables/table-1-injury-and-illness-rates-by-industry-2024-national.htm
"""
import csv, html, json, re, sys
SRC_URL = "https://www.bls.gov/iif/nonfatal-injuries-and-illnesses-tables/table-1-injury-and-illness-rates-by-industry-2024-national.htm"
FOOT = {"7": "rate rounded to zero", "8": "industry added in 2019", "10": "fewer than 15 cases"}
s = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
tb = s[s.find("<tbody"):s.find("</tbody>")]
def text(x):
    x = re.sub(r"<[^>]+>", "", x); return re.sub(r"\s+", " ", html.unescape(x)).strip()
def cell(v):
    notes = re.findall(r"\((\d+)\)", v)
    core = re.sub(r"\(\d+\)", "", v).strip()
    num = float(core) if re.fullmatch(r"\d+(\.\d+)?", core) else None
    return num, notes
rows, owner = [], "private"
for tr in re.findall(r"<tr.*?</tr>", tb, re.S):
    cells = [text(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
    if len(cells) < 7: continue
    name_raw, code = cells[0], cells[1]
    name = re.sub(r"(\(\d+\))+$", "", name_raw).strip()
    if name.startswith("State and local government"): owner = "state_and_local_government"
    elif name == "State government": owner = "state_government"
    elif name == "Local government": owner = "local_government"
    elif name == "Private industry": owner = "private"
    row_owner = "all_ownerships" if name.startswith("All industries including") else owner
    vals, notes = [], set(re.findall(r"\((\d+)\)", name_raw))
    for v in cells[2:7]:
        n, f = cell(v); vals.append(n); notes.update(f)
    rows.append(dict(ownership=row_owner, naics=code, industry=name, trc=vals[0], dart=vals[1], dafw=vals[2], djtr=vals[3], other_recordable=vals[4],
                     footnotes=";".join(sorted(notes, key=int)), footnote_text="; ".join(FOOT[n] for n in sorted(notes, key=int) if n in FOOT)))
# parent fallback (private industry only): nearest ancestor code with a published TRC
priv = {r["naics"]: r for r in rows if r["ownership"] == "private" and r["naics"]}
SECT = {"31": "31-33", "32": "31-33", "33": "31-33", "44": "44-45", "45": "44-45", "48": "48-49", "49": "48-49"}
for r in rows:
    r["benchmark_naics"] = r["benchmark_trc"] = r["benchmark_dart"] = None
    r["is_parent_fallback"] = False
    if r["ownership"] != "private" or not r["naics"]: continue
    c = r["naics"]
    while c:
        k = c if c in priv else SECT.get(c)
        if k and priv.get(k) and priv[k]["trc"] is not None:
            r["benchmark_naics"], r["benchmark_trc"], r["benchmark_dart"] = k, priv[k]["trc"], priv[k]["dart"]
            r["is_parent_fallback"] = (k != r["naics"]); break
        c = "" if "-" in c or len(c) <= 2 else c[:-1]
cols = ["ownership", "naics", "industry", "trc", "dart", "dafw", "djtr", "other_recordable", "footnotes", "footnote_text", "benchmark_naics", "benchmark_trc", "benchmark_dart", "is_parent_fallback"]
with open("data/bls_soii_2024_table1.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in rows: w.writerow({k: ("" if r[k] is None else r[k]) for k in cols})
json.dump({"source": SRC_URL, "survey": "BLS Survey of Occupational Injuries and Illnesses (SOII)", "reference_year": 2024,
           "units": "cases per 100 full-time equivalent workers ((N/EH) x 200,000)", "naics_version": "NAICS 2017 (as published by BLS)",
           "null_means": "not published (does not meet BLS publication guidelines) or not applicable", "columns": cols, "rows": rows},
          open("data/bls_soii_2024_table1.json", "w"), indent=1)
print(len(rows), "rows;", sum(1 for r in rows if r["ownership"] == "private" and r["naics"]), "private rows with NAICS;",
      sum(1 for r in rows if r["is_parent_fallback"]), "use parent fallback")
