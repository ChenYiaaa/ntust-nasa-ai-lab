# Browser UAT

Microsoft Edge 158.0.4370.33 ran under Playwright Core 1.65.1 against real
local Flask and Node listeners. Run `WO-M5-WEB-002/R2` used the commands
listed in [execution](execution.md). The accepted suite recorded zero
uncaught JavaScript exceptions and 17 resource messages. The supplemental
suite recorded zero uncaught exceptions and eight resource messages.
Resource messages came from deliberate error paths or the favicon request.

Each row is a successful case or case group with exit 0. The command key
maps to the actual command and evidence path in the execution report.
The ignored JSON logs retain individual case timestamps and results.

| TEST_CASE_ID | TEST_TYPE | Command | Expected | Actual / HTTP | Evidence |
| --- | --- | --- | --- | --- | --- |
| UI-SELECT | DIRECTLY_EXECUTED | SUP-BROWSER | Train → Test → Train, Units reflect API, stale data cleared | Three Unit option lists matched HTTP 200. Four Units and three Sensors exercised. Sensor change removed chart, rows and Prompt. | supplement.json, selectors.png |
| UI-REVERSED, UI-LOWER, UI-UPPER | DIRECTLY_EXECUTED | SUP-BROWSER | Reject reversed and out-of-bounds ranges | Visible CYCLE_OUT_OF_RANGE, no History request, Copy disabled in each case | supplement.json |
| UI-FRACTION, UI-EMPTY | DIRECTLY_EXECUTED | SUP-BROWSER | Reject fractional and missing number | Visible INVALID_PARAMETER, no History request, Copy disabled in both cases | supplement.json |
| UI-PARITY-TRAIN, UI-PARITY-TEST | DIRECTLY_EXECUTED | REG-BROWSER, RAW-JOIN | Real chart, table and Prompt match source | HTTP 200, exact 20/20 Train and 3/3 Test, chart marks and original locators verified | browser-comparisons.json, raw-joined.json |
| UI-PROMPT-COPY | DIRECTLY_EXECUTED | REG-BROWSER | Nine ordered sections, matching semantics and clipboard | Both real prompts matched identity, Catalog fields, data, provenance, quality statistics and evidence classes. Real copy readback matched with only native CRLF conversion allowed. | browser-regression.log, browser-comparisons.json |
| UI-STALE | CONTROLLED_FIXTURE_TEST | REG-BROWSER | Delay a real response across split change | Loading appeared. The prior response did not populate the new split. Unit and Prompt reset. | browser-regression.log |
| UI-BAD-PROVENANCE, UI-BAD-CATALOG | CONTROLLED_FIXTURE_TEST | REG-BROWSER | Refuse inconsistent source or Catalog input | A missing locator or mismatching Catalog source field left Generate and Copy disabled. | browser-regression.log |
| DATA-NULL, DATA-MISSING, DATA-EMPTY-STRING | CONTROLLED_FIXTURE_TEST | SUP-BROWSER | Reject invalid required values | Individual HTTP 200 fixtures led to error UI, no points and no Prompt. | supplement.json |
| DATA-ZERO | CONTROLLED_FIXTURE_TEST | SUP-BROWSER | Preserve numeric zero | HTTP 200 fixture retained exact zero in canvas, source row and Prompt. | supplement.json |
| DATA-NAN, DATA-INFINITY | CONTROLLED_FIXTURE_TEST | SUP-BROWSER | Reject non-JSON numeric tokens | Individual HTTP 200 fixtures led to error UI, no points and no Prompt. | supplement.json |
| DATA-EMPTY-ARRAY | CONTROLLED_FIXTURE_TEST | SUP-BROWSER | Empty result disables actions | HTTP 200 fixture showed empty result and cleared preview. | supplement.json |
| NET-INFLIGHT | CONTROLLED_FIXTURE_TEST | SUP-BROWSER | Abort pending request after successful query | Loading then NETWORK_ERROR, no HTTP response, preview empty and Copy disabled | supplement.json |
| NET-STOP | DIRECTLY_EXECUTED | SUP-BROWSER | Shut down Backend, then restart | Real proxy HTTP 502, no chart or Prompt and Copy disabled. After restart, HTTP 200 produced a new Prompt. | supplement.json, interruption.png |
| NET-SOURCE-503 | DIRECTLY_EXECUTED | REG-BROWSER | Isolated empty source fails verification | Real HTTP 503 SOURCE_NOT_VERIFIED shown in browser, chart and Prompt unavailable | browser-regression.log, ISO-BACK.log |
| UI-MOBILE | DIRECTLY_EXECUTED | REG-BROWSER | Narrow viewport, keyboard use and real query | 375 px view fit viewport. Keyboard changed split, chart and Prompt rendered, copy readback succeeded. | browser-regression.log |
| BROWSER-CONSOLE | DIRECTLY_EXECUTED | SUP-BROWSER and REG-BROWSER | Zero uncaught exceptions | Zero in both browser runs | supplement.json, browser-regression.log |

Four screenshots were reviewed before inclusion. The initial, selector and
interruption captures display UI state, selection or error text. The redacted
prompt image retains the interaction feedback and controls while hiding
the original chart, table and preview text. The unredacted prompt image is
local-only.
