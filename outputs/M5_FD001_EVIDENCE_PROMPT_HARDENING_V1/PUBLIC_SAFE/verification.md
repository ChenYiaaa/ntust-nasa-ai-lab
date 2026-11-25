# Evidence verification

The deterministic prompt uses exactly nine ordered headings:

1. SECTION A: DATASET & SELECTION
2. SECTION B: SOURCE PROVENANCE
3. SECTION C: COLUMN SEMANTICS
4. SECTION D: OBSERVED DATA
5. SECTION E: DATA QUALITY
6. SECTION F: KNOWN FACTS
7. SECTION G: INFERRED FINDINGS
8. SECTION H: UNKNOWN / NOT ESTABLISHED
9. SECTION I: INSTRUCTIONS TO EXTERNAL AI

Observed rows preserve raw reading precision and all three locators. Section E
labels derived statistics as CALCULATED and reuses the existing `statistics()`
function. Section F records facts from the API and contract, Section G reports
that no additional inference was established, and Section H explicitly marks
fault fields, RUL, Health Score and physical meaning as unknown or unestablished.
The existing Catalog supplies all eight sensor fields. The generator verifies
the matching sensor and column against History and rejects absent or
inconsistent metadata. The unit is rendered as UNKNOWN.

| Real History request | HTTP | Exact raw / API / chart / table / Prompt parity |
| --- | --- | --- |
| Train Unit 1, Sensor 7, Cycles 1–20 | 200 | 20/20 |
| Test Unit 2, Sensor 7, Cycles 3–5 | 200 | 3/3 |

The accepted Backend verifier independently parsed raw TXT and checked values
and locators at zero tolerance. Edge checked the proxy and direct responses,
plotted points, source table and prompt rows. The local artifacts were then
joined for exact decimal comparison of Cycle, reading, logical index,
physical line and raw column 12. Source filename, SHA-256, verified status
and Catalog semantics matched. Independent quality statistics agreed within
absolute tolerance `1e-7`. Single-observation sample deviation and slope
showed N/A.

| Source | SHA-256 matched to M2 |
| --- | --- |
| train_FD001.txt | `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8` |
| test_FD001.txt | `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851` |
| RUL_FD001.txt | `a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca` |

Full prompt and per-record evidence are stored in existing Git-ignored
locations, including `web/fd001/frontend_tests/local_only/browser-comparisons.json`.
