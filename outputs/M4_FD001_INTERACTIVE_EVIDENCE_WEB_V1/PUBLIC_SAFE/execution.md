# Local execution

Fetched and read the governance files at
`c1588424dce747c6b878537621b330c44c6c2972`. This matched both local and fetched
`main`. Verified M3 acceptance, M4 Owner approval, WO-M4-001 MAIN acceptance,
scope extension approval, WEB dispatch and M5's unauthorized status. The
project coordination list showed only the Web Worker active. The index was
empty and the accepted M3 web files matched the baseline.

Windows used Anaconda Python 3.13.9, Flask 3.1.2, Werkzeug 3.1.3,
jsonschema 4.25.0 for Backend tests, Node.js 24.19.0, Playwright Core 1.65.1
and installed Microsoft Edge 158.0.4370.33. The frontend runtime uses Node's
standard library. From the repository root, start Flask first and then the
frontend in separate terminals:

```powershell
python -B web/fd001/backend/api.py --port 8765
node web/fd001/frontend/serve.mjs
```

Verified actual localhost URLs were `http://127.0.0.1:8765` for Flask and
`http://127.0.0.1:8766/` for the browser. Stop from the terminal with Ctrl+C.
During automated Windows verification both server types accepted targeted
Ctrl+Break and shut down cleanly.

| Executed command | Exit | Observation |
| --- | --- | --- |
| `git fetch origin main` with per-command workspace safe.directory | 0 | Expected revision fetched |
| `python -B web/fd001/backend/api.py --port 8765` | 0 | Real positive HTTP traffic, then controlled shutdown |
| `node web/fd001/frontend/serve.mjs` | 0 | Real browser traffic and static/proxy checks, then controlled shutdown |
| `python -B web/fd001/backend/api.py --port 8767 --source-dir <empty test directory>` | 0 | Isolated actual 503, then controlled shutdown |
| `node web/fd001/frontend/serve.mjs` with FD001_BACKEND_PORT=8767 and FD001_FRONTEND_PORT=8768 | 0 | Isolated browser request, then controlled shutdown |
| `python -B web/fd001/tests/test_api.py` | 0 | 20 tests succeeded |
| `node --test web/fd001/frontend_tests/model.test.mjs web/fd001/frontend_tests/prompt.test.mjs` | 0 | Four existing model and four new prompt tests succeeded |
| `node web/fd001/frontend_tests/browser.mjs` with FD001_NEGATIVE_ORIGIN=http://127.0.0.1:8768 | 0 on final run | Existing M3 scenarios and M4 browser checks succeeded |
| Local read-only decimal comparison of Backend and browser JSON evidence | 0 | Train 20/20 and Test 3/3 including source locators |

For reproduction, install the browser driver under ignored
`web/fd001/frontend_tests/local_only` using the command in the
[frontend README](../../../web/fd001/frontend/README.md). Start the default
servers before running UAT. The isolated pair uses an empty directory under
the ignored test path and leaves the verified data files intact.
