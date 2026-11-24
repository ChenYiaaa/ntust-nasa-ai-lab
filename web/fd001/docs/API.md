# FD001 local API

## Run from the repository root

Use Python 3.11+ with Flask 3.1 and Werkzeug 3.1. The tests also require
`jsonschema` 4 and the upstream Gate C validator requires NumPy.
The tested versions are recorded in the [execution log](../../../outputs/M3_FD001_HEALTH_WEBSITE_MVP_V1/api/PUBLIC_SAFE/execution.md).
On Windows, set `$python` to the interpreter in that environment. For the
tested Anaconda installation the PowerShell commands are:

```powershell
$python = Join-Path $env:USERPROFILE 'anaconda3/python.exe'
& $python -B web/fd001/backend/api.py --port 8765
```

The server binds to IPv4 loopback. Stop with Ctrl+C or, on Windows, Ctrl+Break.
Restart to verify a new on-disk snapshot. By default the service opens
`data/FD001/` under the repository root. An alternate directory can be supplied
with `--source-dir`; it must contain the same three pinned files.
Before enabling any data endpoint, Gate C verifies the bytes, telemetry shape
and the ascending Test Unit/RUL mapping. A startup verification failure yields
HTTP 503 on all four routes until the data is restored and the server restarted.

## Endpoints and M2 operations

All paths below use `http://127.0.0.1:8765`. A successful GET returns HTTP 200.

| GET | Data | Gate C source |
| --- | --- | --- |
| `/api/health` | Verified source and read-only service status | Construction of `FD001`, including verification of Train, Test and RUL |
| `/api/catalog` | Available splits, sensor metadata and source version | Contract metadata and `FD001.sensors()` |
| `/api/units?split=test` | Split, sorted observed Unit IDs and count | `FD001.units(split)` |
| `/api/history?split=train&unit=1&sensor=7&start=1&end=20` | Inclusive cycle range, count and ordered source points | `FD001.sensor(split, unit_id, sensor_id, cycle_start, cycle_end)` |

Werkzeug serves the loopback socket, Flask validates HTTP parameters and the
adapter projects Gate C records into the response schema. `train` and `test` are
case-sensitive. Unit IDs are scoped to their split. Each named query parameter
must appear once. Numeric parameters are base-10 integers. M2 validates the
Unit, Sensor and observed Cycle boundaries. A single observed Cycle is a valid
range. A reversed, unobserved or out-of-bounds range yields an error.
The other M2 operations (`unit`, `trend` and `rul`) have no public HTTP route.

## Responses and provenance

[Success schema](success.schema.json) and [error schema](error.schema.json)
use JSON Schema Draft 2020-12. Success contains `status: "ok"`, `data` and
`provenance`. Every success includes the string `data.dataset_id` with value `FD001`.
The following endpoint fields in `data` are required and non-null.

- Health returns string `schema_version` (`1.0.0`), `service` (`ready`) and
  `source_status` (`VERIFIED_LOCAL_SOURCE`). Boolean `source_verified` and
  `read_only` are both true after successful snapshot verification.
- Catalog returns string `schema_version` (`1.0.0`), string array
  `available_splits` (`["train", "test"]`), object array `sensor_catalog` and
  integer `sensor_count` derived from that array (21). String `source_version`
  comes from the accepted dataset metadata (`FD001_SHA256_PINNED_V1`).
  The existing `splits` and `sensors` names alias the canonical arrays.
- Units returns string `split`, integer array `unit_ids` and integer
  `unit_count` derived from the selected split's observed IDs (100 for each
  split in the accepted snapshot).

The common provenance fields give the contract version, source
filenames and content hashes, and snapshot verification status. Health and
Catalog list all three verified files. Catalog identifies the column schema
for its sensor metadata. Units identifies the selected file and Unit ID column.

For History, provenance repeats the query context, identifies the sensor column
and gives the lookup method. Its `source_row_reference` is a JSON Pointer to
`/data/points` in the same response. Each point carries the original Cycle,
finite value, logical record index (nonblank rows), physical line (all lines)
and raw column position. All three locators start at 1. The pair of filename
and SHA-256 identifies the exact bytes to which the locators apply.

### Missing and non-finite values

The current success schemas require concrete values for every field present.
Inapplicable row locators are omitted on file-level responses. Unknown physical
sensor units retain the M2 metadata token `UNKNOWN`. A zero must come from the
source. Missing Cycles trigger `CYCLE_OUT_OF_RANGE`; no points are inserted.
The encoder rejects NaN and both infinities before sending any response bytes.

### Error mapping

Errors contain `status: "error"` and an `error` object with `error_code`,
`message`, `input_context` and `recoverability`. The six M2 codes retain the
contract message, context and recovery action.

| HTTP | Code | Trigger |
| --- | --- | --- |
| 400 | INVALID_PARAMETER | Missing, empty, repeated, unexpected or malformed parameter |
| 400 | INVALID_SPLIT | Unsupported split |
| 404 | UNKNOWN_UNIT / UNKNOWN_SENSOR | ID absent from the selected split or schema |
| 422 | CYCLE_OUT_OF_RANGE | Invalid order or unavailable Cycle |
| 503 | SOURCE_NOT_VERIFIED | Unreadable file, incorrect hash or invalid telemetry structure |
| 503 | RUL_MAPPING_INVALID | Verified RUL records cannot be paired with sorted Test IDs |
| 500 | NON_FINITE_RESULT | Serialization detected a non-finite number |
| Framework HTTP status | HTTP_ERROR | Routing or request error, including unknown path (404) and disallowed method (405) |

## Reproduce the HTTP tests

In a second PowerShell session at the repository root, run:

```powershell
$python = Join-Path $env:USERPROFILE 'anaconda3/python.exe'
$env:FD001_TEST_PORT = '8765'
& $python -B web/fd001/tests/test_api.py
```

With `FD001_TEST_PORT` unset, the suite starts its own loopback listener.
Negative tests always use dedicated local instances. The suite validates live
response schemas, reports counts to the terminal and writes exact comparisons
to a new ignored `tests/local_only/api-*/` directory on each run.

## Verification rule

The independent checker compares the decimal token in the source with the JSON
number parsed as a decimal. Absolute tolerance is 0, relative tolerance is 0.
Unit, sensor, split, cycle order, count, column, record, physical line, filename
and SHA-256 must match exactly. The checker scans binary lines, counts every
physical line and only increments the logical record counter on nonblank lines.
The first five columns contain the Unit, Cycle and three settings, so Sensor 7
is column 12 (1-based). Individual comparisons belong under the ignored
`web/fd001/tests/local_only/` directory.
