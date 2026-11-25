# FD001 evidence prompt delivery

Work order `WO-M4-WEB-001` and scope extension
`WO-M4-WEB-001-SCOPE-EXT-01` extend the accepted local M3 website.
Generate a prompt from the current verified History, review it in the read-only
preview, then use Copy prompt to write it to the local clipboard.

- [Startup and execution](execution.md)
- [Source and prompt verification](verification.md)
- [Browser UAT](browser-uat.md)
- [Initial browser screenshot](browser-initial.png)

The authorized manifest comprises:

- `web/fd001/frontend/` — `README.md`, `app.mjs`, `index.html`, `style.css`,
  `serve.mjs` and the new `prompt.mjs`.
- `web/fd001/frontend_tests/` — `browser.mjs` and the new `prompt.test.mjs`.
- This directory — `README.md`, `execution.md`, `verification.md`,
  `browser-uat.md` and `browser-initial.png`.

Detailed numeric and prompt comparisons are stored under existing Git-ignored
local-only paths. The screenshot shows an empty prompt preview before selection.
