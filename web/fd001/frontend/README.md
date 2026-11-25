# FD001 Health Analysis

Run both commands from the repository root in separate PowerShell terminals.
Use the Python environment described in the existing Backend API instructions
and Node.js 22 or newer.

```powershell
python -B web/fd001/backend/api.py --port 8765
node web/fd001/frontend/serve.mjs
```

Open `http://127.0.0.1:8766/`. Select a split, an engine Unit and a sensor.
After the Cycle range is confirmed, enter the inclusive range and select
**Query history**. Expand **Source records** for the accessible point table
and original locators. Stop each server with Ctrl+C.

## Evidence prompt

After a verified History query, select **Generate evidence prompt** to preview
the observed values, source locators, statistics and analysis instructions.
**Copy prompt** uses the browser clipboard on localhost. If clipboard access
is rejected, the preview remains available for manual selection. The browser
clears the preview when a selection changes or a query starts. Clipboard
writes are explicit user actions. The app keeps the preview in memory and
sends no prompt to an external service.

The preview contains nine ordered sections, from Dataset & Selection to
Instructions to External AI. The generator validates the selected entry
from the already-loaded Catalog against History provenance. An absent or
inconsistent definition disables generation. Observed readings are separate
from derived statistics, inferred findings and unknowns. The current contract
reports the sensor unit as UNKNOWN and supplies no physical interpretation.
The prompt states when fault, RUL and Health Score have not been established.

The browser uses same-origin GET requests for Health, Catalog, Units and
History. The Node server binds to IPv4 loopback and forwards only those four
paths to the Flask loopback server. It preserves upstream status and body and
sends a no-store cache policy. The static allowlist contains only five frontend
assets. The frontend takes observed bounds from the documented
`CYCLE_OUT_OF_RANGE` response for a deliberately reversed probe (1–0) using
the selected split and Unit. A genuine query validates those bounds again in
Flask. The canvas draws one mark per observation, using linear axis scaling.
The accepted service verifies its pinned snapshot at startup.

## Statistics

For observed pairs `(x, y)` where `x` is Cycle and `y` is the sensor reading:

- Count is the number of observations. Missing Count is inclusive requested
  range length minus observed count.
- Minimum and Maximum are the smallest and largest readings. Mean is the sum
  of readings divided by the count.
- Sample standard deviation is the square root of the sum of squared
  deviations from the mean divided by `n − 1`.
- OLS slope with intercept is the sum of centered Cycle times centered value,
  divided by the sum of squared centered Cycles.

A single observation has no sample standard deviation or slope. The UI shows
N/A for both. Missing or non-finite measurement values are rejected.

## Verification

```powershell
node --test web/fd001/frontend_tests/model.test.mjs
node --test web/fd001/frontend_tests/prompt.test.mjs
npm.cmd install --prefix web/fd001/frontend_tests/local_only --no-audit --no-fund playwright-core@1.65.1
node web/fd001/frontend_tests/browser.mjs
python -B web/fd001/tests/test_api.py
```

Keep both default-port servers running for the browser command. The browser
suite uses the installed Microsoft Edge channel. Comparison details are
written under `frontend_tests/local_only/`. The public screenshot is taken
before selecting a dataset or querying any telemetry.

For the real missing-source test, start a second Backend on port 8767 with
`--source-dir` pointing to an empty test directory and a second frontend with
`FD001_BACKEND_PORT=8767` and `FD001_FRONTEND_PORT=8768`. Set
`FD001_NEGATIVE_ORIGIN=http://127.0.0.1:8768` in the Browser UAT terminal.
The browser grants clipboard read and write permission for the default
loopback origin. Windows clipboard readback may encode lines as CRLF.
