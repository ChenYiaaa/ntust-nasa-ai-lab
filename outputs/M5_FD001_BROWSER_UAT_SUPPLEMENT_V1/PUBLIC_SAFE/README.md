# FD001 supplemental browser verification

`WO-M5-WEB-002` independently retests the accepted FD001 website, Evidence
Prompt and error paths. The starting revision was
`39093a0b2c6823158ac2f72a0ce098327a370e88`. This delivery adds evidence only.

- [Execution, startup and exit codes](execution.md)
- [Browser UAT matrix](browser-uat.md)
- [Raw parity, input contracts and security](verification.md)
- [Initial state](screenshots/initial.png), [selectors](screenshots/selectors.png),
  [service interruption](screenshots/interruption.png) and
  [redacted prompt interaction](screenshots/prompt-redacted.png)

Only the four documents and four audited PNGs are included. The prompt
interaction screenshot hides the measurement panels and preview text.
Executable assertions, rather than the redacted image, establish numeric
and clipboard parity. Private logs, temporary harnesses, raw comparisons
and the original Prompt screenshot are in Git-ignored local test storage.

Coverage is Windows Edge, including a 375 px viewport, with clipboard
permissions granted for the loopback origin. Flask verifies the local
snapshot at startup. The fixture cases exercise behavior that does not
occur naturally in the verified FD001 data.
