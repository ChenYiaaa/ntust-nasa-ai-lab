# FD001 frontend browser verification

Work order `WO-M3-WEB-002` used accepted Backend baseline
`c50495ca02814018c8f4c30ae5285c48cf9f2a99` on GitHub `main`. The Worker
fetched this revision, read its three governance files and checked the M2
acceptance, MAIN acceptance of the M3 API and frontend dispatch. The project
showed one active Worker and one worktree. The starting index was empty.

## Execution

Windows, Node.js 24.19.0, Anaconda Python 3.13.9, Playwright Core 1.65.1
and Microsoft Edge 158.0.4370.33 (headless, actual browser engine).

| Command | Exit | Result |
| --- | --- | --- |
| `git fetch origin main` with per-command safe.directory | 0 | Fetched the expected baseline |
| `python -B web/fd001/tests/test_api.py` | 0 | 20 accepted Backend tests ran against local listeners, including all three pinned source hashes |
| `npm.cmd install --prefix web/fd001/frontend_tests/local_only --no-audit --no-fund playwright-core` | 0 | Installed the browser driver locally for tests |
| `node --test web/fd001/frontend_tests/model.test.mjs` | 0 | 4 tests succeeded |
| `python -B web/fd001/backend/api.py --port 8765` | 0 | Verified Backend stopped with Ctrl+Break |
| `node web/fd001/frontend/serve.mjs` | 0 | Frontend on 8766 stopped with Ctrl+Break |
| `python -B web/fd001/backend/api.py --port 8767 --source-dir <empty isolated directory>` | 0 | Missing-source Backend stopped with Ctrl+Break |
| `node web/fd001/frontend/serve.mjs` with FD001_FRONTEND_PORT=8768 and FD001_BACKEND_PORT=8767 | 0 | Isolated frontend stopped with Ctrl+Break |
| `node web/fd001/frontend_tests/browser.mjs` with FD001_NEGATIVE_ORIGIN=http://127.0.0.1:8768 | 0 | All nine reported Browser UAT groups succeeded |

The first browser run exited 1 during initial screenshot saving because the
Windows workspace URL encoded spaces. The test now converts the URL with
`fileURLToPath`. The full suite was rerun on the corrected test.

## Browser observations

| Case | Observed |
| --- | --- |
| Initial load | Health and Catalog HTTP 200. Verified read-only indicator, 21 sensor choices with contract units, no selected Unit and no results. |
| Train Unit 1, Sensor 7, Cycles 1–20 | HTTP 200. 20/20 plotted pairs matched the API with exact equality. Exactly 20 marks drawn. |
| Test Unit 2, Sensor 7, Cycles 3–5 | HTTP 200. 3/3 plotted pairs matched the API with exact equality. Exactly three marks drawn. |
| Single observation | HTTP 200. One mark, sample standard deviation and slope both N/A. |
| Loading and stale result | Deferred a real History response and changed split. Prior results were cleared, Unit reset, and the delayed response did not populate the new selection. |
| Error and empty states | Controlled browser responses exercised six M2 error codes, invalid parameters, HTTP 500, connection abort and a successful empty payload. Reversed input was rejected visibly. |
| Private paths and responsive layout | Private data, path traversal form, unapproved API and server source requests returned 404. POST returned 405. Real upstream 422 status and body matched through the proxy. At 375 px the queried page fit the viewport. Tab and arrow keys operated the split selector. |
| Mobile chart | A live five-point query retained chart, statistics and source parity at the narrow viewport. |
| Isolated source failure | Actual missing-file Backend returned HTTP 503. Proxy preserved it and the browser showed SOURCE_NOT_VERIFIED with the chart hidden. |

The browser test compared the browser-facing History body with a direct request
to Flask, then compared every plotted pair, canvas mark count, displayed
source record and provenance field. A separate calculation checked count,
minimum, maximum, mean, sample standard deviation, OLS slope and missing count
to absolute tolerance `1e-7`. There were zero uncaught JavaScript exceptions.
The audit counted 13 browser resource errors during the intentionally failing
requests and favicon lookup.

## Evidence and scope

[Initial browser screenshot](browser-initial.png) was taken in Edge before
selecting a split. Visual review found no measurements, raw paths, credentials
or personal identifiers. Real measurements and detailed numeric comparison
records are in `web/fd001/frontend_tests/local_only/browser-comparisons.json`,
which Git ignores. The existing Backend regression runner also keeps its
record-level evidence in its own ignored directory.

- `web/fd001/frontend/` contains `index.html`, `style.css`, `app.mjs`,
  `model.mjs`, `serve.mjs` and `README.md`.
- `web/fd001/frontend_tests/` contains `.gitignore`, `model.test.mjs` and
  `browser.mjs`.
- This directory contains `browser-uat.md` and `browser-initial.png`.

The service runs on loopback and uses the accepted Backend's verified startup
snapshot. Cycle limits rely on the current API's structured range rejection.
Browser coverage here is Microsoft Edge at desktop and narrow viewport widths.
