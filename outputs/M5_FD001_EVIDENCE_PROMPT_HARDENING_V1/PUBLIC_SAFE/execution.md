# Startup and execution

The starting local and fetched GitHub `main` both resolved to
`282f9e073303f565a86bdaa59b1712933fe8b906`. The Worker read the three
governance files, confirmed M0–M4 acceptance, M5 Owner and MAIN authorization,
and the explicit WO-M5-001 release. The project coordination list showed
only the dispatched Web Worker active. One worktree and an empty index were
observed. The web files matched the accepted M4 delivery.

Windows ran Anaconda Python 3.13.9, Flask 3.1.2, Werkzeug 3.1.3,
jsonschema 4.25.0 for Backend tests, Node.js 24.19.0, Playwright Core 1.65.1
and installed Microsoft Edge 158.0.4370.33. From the repository root, start
Flask first, then Node, in separate terminals:

```powershell
python -B web/fd001/backend/api.py --port 8765
node web/fd001/frontend/serve.mjs
```

Real requests reached `http://127.0.0.1:8765` and the browser opened
`http://127.0.0.1:8766/`. Stop with Ctrl+C in the terminals. In the automated
Windows run, targeted Ctrl+Break gave exit 0 for each server process.

| Command | Exit | Result |
| --- | --- | --- |
| `git fetch origin main` with workspace-scoped safe.directory | 0 | Expected SHA fetched |
| `Get-FileHash -Algorithm SHA256` for Train, Test and RUL | 0 | Each digest matched its M2 pin |
| Backend and frontend startup commands above | 0 each on shutdown | Real 200 responses over loopback |
| `python -B web/fd001/backend/api.py --port 8767 --source-dir <empty test directory>` | 0 on shutdown | Isolated real 503 |
| `node web/fd001/frontend/serve.mjs` with FD001_BACKEND_PORT=8767 and FD001_FRONTEND_PORT=8768 | 0 on shutdown | Isolated browser request |
| `python -B web/fd001/tests/test_api.py` | 0 | 20 Backend regression tests |
| `node --test web/fd001/frontend_tests/model.test.mjs web/fd001/frontend_tests/prompt.test.mjs` | 0 | Four model and six Prompt tests |
| `node web/fd001/frontend_tests/browser.mjs` with FD001_NEGATIVE_ORIGIN=http://127.0.0.1:8768 | 0 | Existing and extended real browser UAT |
| Read-only decimal comparison of ignored Backend and browser artifacts | 0 | 20 Train and three Test records matched |

To reproduce browser checks, install the test driver as described in the
[frontend instructions](../../../web/fd001/frontend/README.md), start the
two default listeners and run the browser command. The isolated optional
pair above enables the real-503 case using an empty ignored test directory.
The browser test requires permission to write and read the local clipboard.
The Backend verifies a snapshot at startup. Restart it to verify a changed
on-disk source.
