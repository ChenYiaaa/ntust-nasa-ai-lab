# FD001 Evidence Prompt hardening

Work order `WO-M5-WEB-001` adds the required nine-section evidence format
to the accepted M4 generator. The application uses its already-loaded Sensor
Catalog and validates the definition against History provenance. Only a
current verified History response can enable generation or copy.

- [Startup, versions and exit codes](execution.md)
- [Raw-source and prompt verification](verification.md)
- [Browser UAT and limitations](browser-uat.md)
- [Initial-state screenshot](browser-initial.png)

The delivery modifies five files:

- `web/fd001/frontend/prompt.mjs`
- `web/fd001/frontend/app.mjs`
- `web/fd001/frontend/README.md`
- `web/fd001/frontend_tests/prompt.test.mjs`
- `web/fd001/frontend_tests/browser.mjs`

The five new public artifacts comprise this README, the three linked reports
and the screenshot. Detailed prompts and record comparisons stay in the
existing Git-ignored local evidence directories.
