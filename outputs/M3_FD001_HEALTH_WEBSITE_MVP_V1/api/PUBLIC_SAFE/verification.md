# WO-M3-WEB-001 verification

The separately launched local service returned HTTP 200 for Train Unit 1,
Sensor 7, Cycles 1–20. All **20 of 20** observations matched the raw Train TXT
exactly. Test Unit 2, Sensor 7, Cycles 3–5 also matched its own file **3 of 3**.

The verifier in `web/fd001/tests/test_api.py` read the HTTP response over a
loopback socket. Its source oracle opened the TXT independently in binary mode,
hashed all bytes, tokenized nonblank records, and selected records by Unit and
Cycle. It decoded the raw sensor token and the JSON number as decimals. The
predeclared absolute and relative tolerances were both zero. Every returned
point matched on Cycle, sensor value, logical record, physical line and source
column. Both queries had exactly the expected ascending Cycles. The response
also matched the requested split, Unit, Sensor, endpoints, observation count,
filename, digest, column name and position. Sensor 7 occupied raw column 12.

| Source | Independently verified SHA-256 |
| --- | --- |
| train_FD001.txt | `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8` |
| test_FD001.txt | `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851` |
| RUL_FD001.txt | `a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca` |

## API test results

| Checks | Observed result |
| --- | --- |
| Health and catalog | HTTP 200, three source digests and 21 sensor definitions verified |
| Units | HTTP 200, 100 sorted IDs each for Train and Test, with split-specific provenance |
| Train and Test History | HTTP 200, 23 total points reconciled, zero mismatches |
| Five omitted History parameters and malformed queries | HTTP 400, INVALID_PARAMETER |
| Invalid split | HTTP 400, INVALID_SPLIT |
| Unknown Unit and Sensor | HTTP 404, UNKNOWN_UNIT and UNKNOWN_SENSOR |
| Out-of-bounds and reversed ranges | HTTP 422, CYCLE_OUT_OF_RANGE |
| Missing file and incorrect digest | All four endpoints returned HTTP 503, SOURCE_NOT_VERIFIED, for each isolated fixture |
| Invalid RUL mapping | Isolated test shortened the in-memory RUL records passed into the real mapper; HTTP 503, RUL_MAPPING_INVALID |
| Non-finite output and null handling | Injected NaN, positive and negative infinity each yielded strict JSON and HTTP 500, NON_FINITE_RESULT. Success schema requires numeric points and original locators. |
| Method and routing | HTTP 405 for POST, HTTP 404 for unknown path |

All 17 test methods succeeded. Every tested response passed its success or error
schema. M2's 35 checks also succeeded against the original files. Both regenerated
public JSON results matched their accepted Gate C counterparts byte for byte.
The [execution log](execution.md) records the commands and exit codes.
Detailed comparisons, including both sides of each numeric comparison, are
kept under the student's ignored local evidence directory.
