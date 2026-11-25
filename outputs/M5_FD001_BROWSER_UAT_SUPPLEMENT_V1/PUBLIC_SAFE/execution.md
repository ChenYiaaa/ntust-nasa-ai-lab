# Execution

Run identifier `WO-M5-WEB-002/R2` applies to the successful execution and
the associated screenshots. The local HEAD, fetch and independent remote
query matched `39093a0b2c6823158ac2f72a0ce098327a370e88`. The Worker read
all three governance files, checked M0–M4 acceptance and M5 release,
confirmed MAIN acceptance of WO-M5-001, WO-M5-WEB-001 and WO-M5-002, and
confirmed the MAIN Worker hold acknowledgment and released write lock.
WO-M5-003 remained on hold. The coordination list showed this Worker
as the only active project Worker.

`git status --short`, `git diff --name-status`, `git diff --cached --name-status`,
`git ls-files --others --exclude-standard`, `git worktree list`,
`git rev-parse HEAD` and `git ls-remote origin refs/heads/main` were inspected.
There was one worktree, zero staged or tracked changes, 13 pre-existing
untracked file paths, and no public output collision. The full local manifest
is retained in ignored `preflight.txt`. All tracked files matched the fetched
revision before work. The 13 pre-existing untracked files were outside the
authorized output path.

## Runtime and commands

Windows used the existing Anaconda base interpreter `python.exe` directly,
without changing PATH. It reported Python 3.13.9, Flask 3.1.2, Werkzeug 3.1.3
and jsonschema 4.25.0. Node.js was 24.19.0, Playwright Core 1.65.1, and the
installed Microsoft Edge browser reported 158.0.4370.33.
The public command examples use `python` for that Anaconda interpreter.

```powershell
python -B web/fd001/backend/api.py --port 8765
node web/fd001/frontend/serve.mjs
```

Run from the repository root, Flask first. Live HTTP health succeeded at
`http://127.0.0.1:8765/api/health`, and Edge navigated to
`http://127.0.0.1:8766/`. Stop interactively with Ctrl+C. The test harness
used targeted Windows Ctrl+Break and waited for each owned process exit.

All evidence paths below are relative to the ignored run directory
`web/fd001/frontend_tests/local_only/m5-uat-supplement/` unless stated
otherwise. All entries are DIRECTLY_EXECUTED.

| Test ID | Command | Expected / actual | Exit | Evidence |
| --- | --- | --- | --- | --- |
| BACK-START, FRONT-START | Startup commands above | HTTP 200 each / HTTP 200 each | 0 on shutdown | BACK.log, FRONT.log, execution.json |
| ISO-BACK-START, ISO-FRONT-START | Same commands on 8767/8768 with empty test source and isolated proxy | HTTP 503 / HTTP 503 at both listeners | 0 on shutdown | ISO-BACK.log, ISO-FRONT.log |
| BACK-STOP, BACK-RESTORED-START, BACK-RESTORED-STOP | Targeted Ctrl+Break, restart the original Backend command, then Ctrl+Break | Exit 0 and HTTP 200 after restart / both exits 0 and HTTP 200 | 0 | execution.json, BACK-RESTORED.log |
| REG-BACK | `python -B web/fd001/tests/test_api.py` with FD001_TEST_PORT=8765 | 20 tests / 20 successful | 0 | backend-regression.log |
| REG-NODE | `node --test web/fd001/frontend_tests/model.test.mjs web/fd001/frontend_tests/prompt.test.mjs` | 10 tests / 10 successful | 0 | node-regression.log |
| REG-BROWSER | `node --import <ignored loader file URL> web/fd001/frontend_tests/browser.mjs` | Existing scenarios / all successful | 0 | browser-regression.log, browser-comparisons.json |
| SUP-BROWSER | `node <ignored run.mjs>` | Supplemental cases / 16 successful | 0 | supplement.json, browser-supplement.log |
| RAW-JOIN | `python -B <ignored compare.py>` | 20 Train and 3 Test exact / 20 and 3 exact | 0 | raw-joined.json |
| BIND | `netstat -ano -p tcp` during execution | Loopback only / all four owned listeners on 127.0.0.1 | 0 | R2 listener observation |

The ignored runner was invoked as `python -B <ignored execute.py>`.
It records UTC timestamps and actual process parameters in `execution.json`.
The browser regression loader rewrites only the accepted script's two
output destinations in memory to protect the tracked M5 screenshot and
save new results in this run directory. It leaves all assertions unchanged.
The first runner attempt exited 1 before browser execution because Node
treated the Windows drive letter as an import scheme. The ignored runner
was corrected to use a file URL. The first log was retained and the complete
suite was rerun with exit 0. No product or tracked test file was changed.
