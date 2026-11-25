# Prompt verification

| Real query | HTTP | Raw TXT, API, chart, source table and prompt |
| --- | --- | --- |
| Train Unit 1, Sensor 7, Cycles 1–20 | 200 | 20/20 exact |
| Test Unit 2, Sensor 7, Cycles 3–5 | 200 | 3/3 exact |

The accepted Backend test used independent binary TXT tokenization and decimal
comparison at zero tolerance. Browser UAT compared the live proxy response
with direct Flask HTTP, actual plotted pairs, visible table rows and every
prompt row. A read-only comparison then joined the two local test artifacts
and verified exact decimal equality of Cycle, value, record index, physical
line and column. Both fixture queries used source column 12. Source filename,
split, Unit, Sensor, Cycle range, SHA-256 and verified status agreed across
the recorded API and displayed evidence. Health regression matched Train,
Test and RUL source hashes to the accepted pins.

Independent browser calculations matched all displayed and prompt statistics
to absolute tolerance `1e-7`. Single-observation deviation and slope were N/A.
Prompt unit tests verified deterministic generation, signed decimals, preserved
zero, selection mismatch rejection and invalid source/measurement handling.
The generator accepts the verified snapshot's provenance and checks its shape
and relationships. Actual byte hashing remains the Backend's responsibility.

The commit evidence contains counts, methods, results and a screenshot of an
empty preview. Full prompts and raw-value comparisons are in ignored local
evidence, including `web/fd001/frontend_tests/local_only/browser-comparisons.json`.
