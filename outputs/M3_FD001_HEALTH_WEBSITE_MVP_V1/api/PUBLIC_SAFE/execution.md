# Local execution record

## WO-M3-WEB-001-CORR-01

Fetched `main` and read its `AGENTS.md`, `ROADMAP.md` and `WORK_ITEM.md`.
Remote, fetch and local refs initially agreed at
`8fc76574796129619be4dbe5c57f7a2269b0ac05`. Confirmed the M3 release,
MAIN correction authorization and WEB dispatch. The workspace had one worktree,
an empty index, pre-existing untracked data and research files, and one active
project Worker.

The six-file correction modifies:

- `web/fd001/backend/api.py`
- `web/fd001/docs/API.md`
- `web/fd001/docs/success.schema.json`
- `web/fd001/tests/test_api.py`
- `outputs/M3_FD001_HEALTH_WEBSITE_MVP_V1/api/PUBLIC_SAFE/execution.md`
- `outputs/M3_FD001_HEALTH_WEBSITE_MVP_V1/api/PUBLIC_SAFE/verification.md`

The commands used the same Anaconda Python 3.13.9 environment as the original
execution below.

| Command | Exit | Result |
| --- | --- | --- |
| `git fetch origin main` with per-command workspace safe.directory | 0 | Expected baseline fetched |
| `git rev-parse FETCH_HEAD HEAD origin/main` and the three `git show FETCH_HEAD:<governance file>` requests | 0 each | Refs agreed and governance files read |
| `Get-FileHash -Algorithm SHA256` on Train, Test and RUL | 0 | All three work-order hashes matched |
| `python -B outputs/M2_FD001_DATA_CONTRACT_V1/gate_c/PUBLIC_SAFE/validate_contract.py --output web/fd001/tests/local_only/m2-corr-01` with PYTHONDONTWRITEBYTECODE=1 | 0 | 35 checks succeeded, hashes stable |
| `python -B web/fd001/backend/api.py --port 8765` | 0 | Separate loopback server served HTTP requests and exited on a targeted Windows Ctrl+Break |
| `python -B web/fd001/tests/test_api.py` with FD001_TEST_PORT=8765 | 0 | 20 methods succeeded, including 33 negative schema cases |
| Read-only comparison of evidence summaries and History schema against the baseline | 0 | Train 20/20 and Test 3/3 exact, two M2 JSON outputs byte-identical, History definition identical |

The server verifies a snapshot on startup and needs a restart to verify later
on-disk changes. Per-record evidence is under the ignored
`web/fd001/tests/local_only/` directory. See the [correction results](verification.md).

## Original execution

WO-M3-WEB-001 ran on Windows with Anaconda Python 3.13.9, Flask 3.1.2,
Werkzeug 3.1.3, jsonschema 4.25.0 and NumPy 2.3.5. Commands below use
`python` to denote the tested environment's interpreter.

| Command or check | Exit | Observation |
| --- | --- | --- |
| Repository-scoped `git -c safe.directory=<workspace> fetch origin main` | 0 | The first fetch encountered Git's ownership check (exit 1). The single-command directory setting permitted the fetch. |
| `git rev-parse FETCH_HEAD HEAD origin/main` | 0 | All three resolved to `ce90203ff78dd6c0276f8637c268c1b40d6d6f19`. |
| `git show FETCH_HEAD:AGENTS.md`, `ROADMAP.md` and `WORK_ITEM.md` via the same revision | 0 each | M2 Gates A/B/C accepted, contract 1.0.0, M3 conditional release documented. MAIN's subsequent acceptance on this SHA and WEB's recheck and dispatch were confirmed separately. |
| `Get-FileHash -Algorithm SHA256` for the three authorized local inputs | 0 | Three pinned digests matched. |
| `python -B outputs/M2_FD001_DATA_CONTRACT_V1/gate_c/PUBLIC_SAFE/validate_contract.py --output web/fd001/tests/local_only/m2` | 0 | 35 checks succeeded. Child interpreters inherited PYTHONDONTWRITEBYTECODE=1. |
| `python -B web/fd001/backend/api.py --port 8765` | 0 on final run | Bound 127.0.0.1 and served live requests. Final server exited cleanly on a targeted Windows Ctrl+Break. |
| `python -B web/fd001/tests/test_api.py` with FD001_TEST_PORT=8765 | 0 | Final run executed 17 tests against the separately launched server and isolated failure instances. |

During the first run the terminal's interrupt did not stop the test listener.
The worker terminated that process after the successful HTTP tests (process exit
15, shell exit 1), added explicit console signal handling and repeated startup,
all tests and shutdown. The final run above includes the signal-handling change.

The workspace had one Git worktree and no staged or tracked changes at intake.
The project worker inventory showed only the dispatched Web worker active.
Pre-existing untracked research/data paths stayed outside the delivery manifest.
The enclosing Git commit records the changed files. The Worker return records
the commit SHA and the independently queried post-push remote SHA.
