# Local execution record

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
