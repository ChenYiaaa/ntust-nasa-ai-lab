# Verification

Run `WO-M5-WEB-002/R2` repeated zero-tolerance comparisons for Train Unit 1,
Sensor 7, Cycles 1–20 and Test Unit 2, Sensor 7, Cycles 3–5. The accepted
Backend suite independently opened the actual TXT files read-only and
tokenized their rows. The browser compared live direct/proxy HTTP responses,
canvas marks, actual table rows and Prompt rows. Joining fresh private
Backend and browser evidence verified **20/20 Train** and **3/3 Test**
exact values, logical record indices, physical lines and column 12.
Dataset FD001, selected Split, Unit, Sensor, Cycle range, source name,
verified digest and contract version 1.0.0 matched. Independent statistics
agreed at absolute tolerance `1e-7`. Both real Prompts preserved Catalog
metadata, nine ordered headings and distinct evidence classes. Fault status,
cause, RUL and Health Score remained unestablished or unestimated.

| Source | SHA-256 matched to M2 |
| --- | --- |
| train_FD001.txt | `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8` |
| test_FD001.txt | `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851` |
| RUL_FD001.txt | `a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca` |

## Direct API Error Schema

Each row was directly executed against live Flask during R2 by the ignored
`execute.py` runner. The actual status/code matched the expected pair and
the full payload validated against the accepted Error Schema Draft 2020-12.
Each case recorded exit 0 and PASS, with the named JSON body and individual
timestamp under the ignored evidence directory. The browser separately
verified that prevented invalid inputs send no HTTP History request.

| TEST_CASE_ID | Request variation | Expected and observed | Evidence |
| --- | --- | --- | --- |
| API-SPLIT | GET invalid split | 400 INVALID_SPLIT | api-SPLIT.json |
| API-UNIT | GET unknown Unit | 404 UNKNOWN_UNIT | api-UNIT.json |
| API-SENSOR | GET unknown Sensor | 404 UNKNOWN_SENSOR | api-SENSOR.json |
| API-CYCLE | GET text Cycle | 400 INVALID_PARAMETER | api-CYCLE.json |
| API-REVERSED | GET start greater than end | 422 CYCLE_OUT_OF_RANGE | api-REVERSED.json |
| API-LOWER | GET start below minimum | 422 CYCLE_OUT_OF_RANGE | api-LOWER.json |
| API-UPPER | GET end above maximum | 422 CYCLE_OUT_OF_RANGE | api-UPPER.json |
| API-FRACTION | GET noninteger Cycle | 400 INVALID_PARAMETER | api-FRACTION.json |
| API-MISSING | GET missing required end | 400 INVALID_PARAMETER | api-MISSING.json |
| API-METHOD | POST | 405 HTTP_ERROR | api-METHOD.json |

The accepted success schema has no nullable History measurement field. The
Catalog's `nullable: false` is Boolean metadata, and the physical sensor
unit remains `UNKNOWN`. The browser fixtures tested null, missing key,
empty string, zero, invalid NaN and Infinity tokens and an empty array
individually. Only valid zero remained a numeric observation. No case
fabricated or interpolated a missing observation.

The browser used actual clipboard permissions on the local origin. It
clicked Copy for both real queries, waited for success and read the clipboard.
Only native Windows LF-to-CRLF conversion was accepted. No request to an
external LLM is made by the generation or copy handlers.

The real shutdown/restart case observed proxy 502 then successful recovery
with HTTP 200. The isolated missing-source case observed real 503. Browser
fixtures independently exercised a disconnected request and a delayed stale
response. Inapplicable or obsolete Prompt content was cleared or disabled.

Security regression checked the five existing static responses and compared
each of the four API proxy responses against direct Flask. Unknown routes,
private paths and encoded traversal returned 404. Non-GET returned 405.
Invalid Host returned 400. The five asset responses retained no-store and
nosniff. Listener inspection confirmed the actual loopback bindings.
See the [browser case matrix](browser-uat.md) for fixture and real-run distinctions.
